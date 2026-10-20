"""The Job Board: live remote-developer jobs from free job-board APIs, browsable by course language.

Listings come from Himalayas and Jobicy (see app/integrations/jobs/boards.py). Each language's feed is
fetched at most every few hours and stored, so the boards see a handful of requests a day. If a board is
down, the stored listings keep showing (flagged as stale).

Applying happens on the board's site. Logicraft helps prepare the resume and cover note, then keeps a
free tracker of where the player applied and how it's going.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from app.core.clock import as_utc, new_id, utcnow
from app.core.errors import ConflictError, NotFoundError, UnprocessableError
from app.domain import resume_ai
from app.domain.economy import RESUME_AI_COST
from app.domain.jobs import days_ago
from app.domain.languages import LANGUAGES
from app.integrations.jobs.boards import JobBoard, JobBoardUnavailable
from app.repositories.jobs import JobFeedRepository, JobListingRepository
from app.repositories.player_content import JobApplicationRepository, ResumeRepository
from app.schemas.jobs import (
    ApplicationStatus,
    ApplyRequest,
    ApplyResponse,
    Job,
    JobApplication,
    JobApplicationDoc,
    JobBoardInfo,
    JobList,
    JobLogo,
    JobSnapshot,
)
from app.schemas.resumes import (
    CoverNoteRequest,
    ImproveBulletRequest,
    JobMatch,
    MatchRequest,
    ResumeDataRequest,
    SkillsRequest,
    SkillsResult,
    TailorRequest,
    TailorResponse,
    TextResult,
)
from app.services.users import UserService
from app.services.wallet import WalletService

logger = logging.getLogger(__name__)

# Both boards refresh about daily and ask callers to cache.
FEED_TTL = timedelta(hours=8)
RETRY_AFTER = timedelta(minutes=30)
# Listings not seen again in a refresh disappear after this.
KEEP_FOR = timedelta(days=4)
MAX_LISTED = 150
# One refresh per language at a time, across requests (containers are per request).
_REFRESH_LOCKS: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
_REFRESH_ALL_SLOTS = 4


def job_text(job: Job) -> str:
    """The text Quest AI reads when matching a resume to a job."""
    return "\n".join([job.role, job.description, ", ".join(job.tags)])


def to_job(doc: dict[str, Any], now: datetime) -> Job:
    posted = as_utc(doc["posted_at"])
    return Job(
        id=doc["_id"],
        company=doc["company"],
        role=doc["role"],
        location=doc["location"],
        work_mode=doc["work_mode"],
        employment=doc["employment"],
        level=doc["level"],
        salary=doc.get("salary"),
        posted_at=posted,
        posted_days_ago=days_ago(posted, now),
        logo=JobLogo(sprite=doc.get("logo_sprite", "briefcase"), color=doc.get("logo_color", "#a78bfa")),
        summary=doc.get("summary", ""),
        description=doc.get("description", ""),
        tags=doc.get("tags", []),
        languages=doc.get("languages", []),
        source=doc["source"],
        source_url=doc["source_url"],
        apply_url=doc["apply_url"],
    )


def _application(doc: JobApplicationDoc) -> JobApplication:
    return JobApplication(**doc.model_dump(exclude={"user_id"}))


def feed_due(state: dict[str, Any] | None, now: datetime) -> bool:
    """A feed is fetched again after FEED_TTL, or RETRY_AFTER when its last fetch failed."""
    if not state:
        return True
    if state.get("ok"):
        return as_utc(state["fetched_at"]) <= now - FEED_TTL
    return as_utc(state["attempted_at"]) <= now - RETRY_AFTER


class JobService:
    def __init__(
        self,
        boards: list[JobBoard],
        listings: JobListingRepository,
        feeds: JobFeedRepository,
        applications: JobApplicationRepository,
        resumes: ResumeRepository,
        wallet: WalletService,
    ):
        self.boards = boards
        self.listings = listings
        self.feeds = feeds
        self.applications = applications
        self.resumes = resumes
        self.wallet = wallet

    # --- Feeds -----------------------------------------------------------------------------------------

    async def _refresh(self, language: str) -> None:
        """Fetches the language's feeds that are due. A board that fails keeps its stored listings."""
        async with _REFRESH_LOCKS[language]:
            states = await self.feeds.all()
            now = utcnow()
            due = [b for b in self.boards if feed_due(states.get(f"{b.name}:{language}"), now)]

            async def fetch(board: JobBoard) -> None:
                key = f"{board.name}:{language}"
                try:
                    postings = await board.search(language)
                except JobBoardUnavailable as exc:
                    logger.warning("Job board %s failed for %s: %s", board.name, language, exc)
                    await self.feeds.record(key, attempted_at=now, ok=False, count=0)
                    return
                # Board searches are fuzzy: keep only jobs that really ask for one of the course languages.
                relevant = [p for p in postings if p.languages]
                await self.listings.upsert_many(relevant, keep_until=now + KEEP_FOR)
                await self.feeds.record(key, attempted_at=now, ok=True, count=len(relevant))

            await asyncio.gather(*(fetch(b) for b in due))

    async def _refresh_all(self) -> None:
        slots = asyncio.Semaphore(_REFRESH_ALL_SLOTS)

        async def one(language: str) -> None:
            async with slots:
                await self._refresh(language)

        await asyncio.gather(*(one(lang) for lang in LANGUAGES))

    # --- Listings ----------------------------------------------------------------------------------------

    async def list_jobs(
        self,
        *,
        language: str | None,
        work_mode: str | None,
        employment: str | None,
        level: str | None,
        search: str | None,
    ) -> JobList:
        if language and language not in LANGUAGES:
            raise NotFoundError(f"There's no {language} track.")
        await (self._refresh(language) if language else self._refresh_all())

        now = utcnow()
        filters: dict[str, Any] = {"expires_at": {"$gt": now}}
        if language:
            filters["languages"] = language
        filters |= {k: v for k, v in {"work_mode": work_mode, "employment": employment, "level": level}.items() if v}
        docs = await self.listings.search(filters, limit=600)

        needle = (search or "").strip().lower()
        if needle:
            docs = [
                d
                for d in docs
                if needle
                in " ".join([d["role"], d["company"], d["location"], d.get("summary", ""), *d.get("tags", [])]).lower()
            ]
        # Boards post one role once per country; list it once (the newest post).
        seen: set[tuple[str, str]] = set()
        docs = [d for d in docs if (key := (d["company"].lower(), d["role"].lower())) not in seen and not seen.add(key)]
        if language:
            # Jobs that name the language in their title first; newest first within each group.
            docs.sort(key=lambda d: language not in d.get("title_languages", []))

        states = await self.feeds.all()
        keys = [f"{b.name}:{lang}" for b in self.boards for lang in ([language] if language else LANGUAGES)]
        fetched = [as_utc(states[k]["fetched_at"]) for k in keys if states.get(k, {}).get("fetched_at")]
        return JobList(
            jobs=[to_job(d, now) for d in docs[:MAX_LISTED]],
            sources=[JobBoardInfo(name=b.name, url=b.home) for b in self.boards],
            updated_at=min(fetched) if fetched else None,
            stale=any(k in states and not states[k].get("ok") for k in keys),
        )

    async def get(self, job_id: str) -> Job:
        doc = await self.listings.get(job_id)
        now = utcnow()
        if not doc or as_utc(doc["expires_at"]) <= now:
            raise NotFoundError("This listing has closed or expired.")
        return to_job(doc, now)

    # --- Applications --------------------------------------------------------------------------------------

    async def list_applications(self, user_id: str) -> list[JobApplication]:
        return [_application(d) for d in await self.applications.for_user(user_id)]

    async def apply(self, user_id: str, job_id: str, body: ApplyRequest) -> ApplyResponse:
        """Records an application the player is making on the board's site. Free: XP only pays for AI help."""
        job = await self.get(job_id)
        if await self.applications.find(user_id, job_id):
            raise ConflictError("You're already tracking an application for this job.")
        resume = await self.resumes.get(user_id, body.resume_id)
        if not resume:
            raise NotFoundError("Resume not found.")
        sent = body.resume or resume.data
        doc = JobApplicationDoc(
            id=new_id(),
            user_id=user_id,
            job_id=job.id,
            job=JobSnapshot(
                id=job.id,
                role=job.role,
                company=job.company,
                location=job.location,
                source=job.source,
                apply_url=job.apply_url,
                logo=job.logo,
            ),
            applied_at=utcnow(),
            resume=sent,  # snapshot exactly as prepared
            template_id=resume.template_id,
            resume_title=resume.title,
            cover_note=body.cover_note,
            tailored=body.tailored,
            match_score=resume_ai.match_job(sent, job_text(job)).score if body.tailored else None,
            xp_spent=body.ai_xp_spent,
        )
        await self.applications.insert(doc)
        return ApplyResponse(application=_application(doc), balance=await self.wallet.balance(user_id))

    async def update_status(self, user_id: str, application_id: str, status: ApplicationStatus) -> JobApplication:
        doc = await self.applications.set_status(user_id, application_id, status, utcnow())
        if not doc:
            raise NotFoundError("Application not found.")
        return _application(doc)


class ResumeAIService:
    """Quest AI's resume actions. Each charges XP up front; matching a resume against a job is free."""

    def __init__(self, users: UserService, jobs: JobService, wallet: WalletService):
        self.users = users
        self.jobs = jobs
        self.wallet = wallet

    async def _facts(self, user_id: str) -> resume_ai.LearnerFacts:
        p = await self.users.profile(user_id)
        return resume_ai.LearnerFacts(
            problems_solved=p.stats.problems_solved,
            accuracy=p.stats.accuracy,
            rank=p.rank,
            league_label=p.league.label,
            longest_streak=p.stats.longest_streak,
        )

    async def _job_description(self, job_id: str | None, job_description: str | None) -> tuple[str, Job | None]:
        if job_id:
            job = await self.jobs.get(job_id)
            return job_text(job), job
        if job_description and job_description.strip():
            return job_description, None
        raise UnprocessableError("Pick a job or paste a job description.")

    async def improve_bullet(self, user_id: str, body: ImproveBulletRequest) -> TextResult:
        balance = await self.wallet.spend(user_id, RESUME_AI_COST["bullet"], "Resume AI: improve bullet")
        return TextResult(text=resume_ai.improve_bullet(body.text), balance=balance)

    async def summary(self, user_id: str, body: ResumeDataRequest) -> TextResult:
        facts = await self._facts(user_id)
        balance = await self.wallet.spend(user_id, RESUME_AI_COST["summary"], "Resume AI: summary")
        return TextResult(text=resume_ai.generate_summary(body.data, facts), balance=balance)

    async def skills(self, user_id: str, body: SkillsRequest) -> SkillsResult:
        balance = await self.wallet.spend(user_id, RESUME_AI_COST["skills"], "Resume AI: suggest skills")
        return SkillsResult(skills=resume_ai.suggest_skills(body.existing), balance=balance)

    async def tailor(self, user_id: str, body: TailorRequest) -> TailorResponse:
        description, job = await self._job_description(body.job_id, body.job_description)
        facts = await self._facts(user_id)
        balance = await self.wallet.spend(user_id, RESUME_AI_COST["tailor"], "Resume AI: tailor to job")
        result = resume_ai.tailor_to_job(body.data, description, facts, (job.role, job.company) if job else None)
        return TailorResponse(
            result=result, tailored_data=resume_ai.apply_tailoring(body.data, result), balance=balance
        )

    async def cover_note(self, user_id: str, body: CoverNoteRequest) -> TextResult:
        job = await self.jobs.get(body.job_id)
        facts = await self._facts(user_id)
        balance = await self.wallet.spend(
            user_id, RESUME_AI_COST["cover_note"], f"Resume AI: cover note for {job.company}"
        )
        return TextResult(
            text=resume_ai.write_cover_note(body.data, job.role, job.company, job_text(job), facts), balance=balance
        )

    async def match(self, body: MatchRequest) -> JobMatch:
        description, _ = await self._job_description(body.job_id, body.job_description)
        return resume_ai.match_job(body.data, description)
