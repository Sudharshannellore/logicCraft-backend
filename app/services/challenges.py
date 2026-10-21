"""Live challenges built from Exercism, for all 13 course languages.

- Daily Challenge, Speed Round and Weekly Boss rotate on a UTC schedule (see app/domain/challenges.py).
  Every player gets the same exercises; times are measured on the server from when the player starts.
- Zone bosses guard the gates on each course map: a few exercises in the course's language at the
  zone's level. Beating one opens the next zone.

Python, JavaScript, TypeScript and SQL are graded here against the exercise's own tests. For the other
languages the challenge links to Exercism's free online editor; it isn't timed and pays no bonus.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.core.clock import as_utc, utcnow
from app.core.errors import ConflictError, NotFoundError, ServiceUnavailableError, UnprocessableError
from app.domain.challenges import (
    KINDS,
    RULES,
    ZONE_LEVELS,
    ZONE_MINUTES_PER_ROUND,
    Candidate,
    ChallengeKind,
    challenge_id,
    parse_id,
    period_bounds,
    period_of,
    pick_boss,
    shortlist,
)
from app.domain.languages import LANGUAGES, LanguageInfo
from app.integrations.exercism.client import ExerciseSummary, ExercismClient, ExercismUnavailable, website_url
from app.repositories.challenges import ChallengeAttemptRepository
from app.repositories.exercism_cache import ExercismCacheRepository
from app.repositories.users import UserRepository
from app.schemas.challenges import (
    ChallengeAttempt,
    ChallengeRunner,
    ChallengeStage,
    ChallengeSubmitResult,
    LiveChallenge,
)
from app.schemas.learning import LessonCompletion
from app.services.learning import LearningService
from app.services.library import LibraryService, difficulty_for
from app.services.quests import ProgressTracker
from app.services.wallet import WalletService

# How many shortlisted exercises to test-run before settling on one.
MAX_CHECKS = 6
CHECK_TTL = 14 * 24 * 60 * 60
ZONE_PICK_TTL = 60 * 24 * 60 * 60
FASTEST_SHOWN = 5
# A Speed Round won this fast counts toward the "Speed Coder" achievement.
SPEED_RECORD_SECONDS = 120


@dataclass
class _Spec:
    id: str
    kind: str
    title: str
    description: str
    info: LanguageInfo
    time_limit_minutes: int
    bonus_xp: int
    retry: bool
    stages: list[ExerciseSummary]
    period: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    boss_name: str | None = None
    boss_sprite: str | None = None
    course_id: str | None = None
    boss_id: str | None = None
    # Zone bosses: still behind uncleared topics / already beaten (maybe on exercism.org).
    locked: bool = False
    defeated: bool = False
    slugs: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self.slugs = [s.slug for s in self.stages]


class ChallengeService:
    def __init__(
        self,
        client: ExercismClient,
        cache: ExercismCacheRepository,
        library: LibraryService,
        learning: LearningService,
        attempts: ChallengeAttemptRepository,
        users: UserRepository,
        wallet: WalletService,
        tracker: ProgressTracker,
    ):
        self.client = client
        self.cache = cache
        self.library = library
        self.learning = learning
        self.attempts = attempts
        self.users = users
        self.wallet = wallet
        self.tracker = tracker

    # --- Picking exercises --------------------------------------------------------------------------

    async def _works(self, info: LanguageInfo, slug: str) -> bool:
        """The starter code runs here and fails its tests, so the exercise is a real (and fair) challenge."""
        if not self.library.gradable(info.id):
            return True
        key = f"check:{info.exercism_track}:{slug}"
        verdict = await self.cache.get(key)
        if verdict is None:
            try:
                verdict = await self.library.starter_fails(info.id, slug)
            except Exception:  # noqa: BLE001 — any failure just means "pick another"
                verdict = False
            await self.cache.put(key, verdict, ttl_seconds=CHECK_TTL)
        return bool(verdict)

    async def _stages(
        self, info: LanguageInfo, key: str, seed: str, bands: tuple[tuple[int, int], ...], ttl: int
    ) -> list[ExerciseSummary]:
        """The challenge's exercises. Picked once, then remembered until the challenge rotates out."""
        try:
            pool = await self.client.exercises(info.exercism_track)
        except ExercismUnavailable as exc:
            raise ServiceUnavailableError("Exercism can't be reached right now — try again in a minute.") from exc
        by_slug = {e.slug: e for e in pool}

        cached = await self.cache.get(f"pick:{key}")
        if cached and all(slug in by_slug for slug in cached):
            return [by_slug[slug] for slug in cached]

        candidates = [Candidate(e.slug, e.difficulty, e.topics) for e in pool]
        chosen: list[str] = []
        for i, band in enumerate(bands):
            order = shortlist(candidates, f"{seed}#{i}", band, exclude=set(chosen))
            pick = None
            for slug in order[:MAX_CHECKS]:
                if await self._works(info, slug):
                    pick = slug
                    break
            if pick or order:
                chosen.append(pick or order[0])
        if not chosen:
            raise ServiceUnavailableError(f"Exercism has no {info.name} exercises right now.")
        await self.cache.put(f"pick:{key}", chosen, ttl_seconds=ttl)
        return [by_slug[slug] for slug in chosen]

    # --- Specs -----------------------------------------------------------------------------------------

    @staticmethod
    def _language(language_id: str) -> LanguageInfo:
        info = LANGUAGES.get(language_id)
        if not info:
            raise NotFoundError(f"There's no {language_id} track.")
        return info

    async def _periodic(self, kind: ChallengeKind, period: str, language_id: str) -> _Spec:
        info = self._language(language_id)
        starts, ends = period_bounds(kind, period)
        if starts > utcnow():
            raise NotFoundError("That challenge hasn't started yet.")
        rule = RULES[kind]
        cid = challenge_id(kind, period, language_id)
        ttl = int((ends - utcnow()).total_seconds()) + 2 * 24 * 60 * 60
        stages = await self._stages(info, cid, cid, rule.stages, max(ttl, 60))
        boss_name, boss_sprite = pick_boss(cid) if kind == "boss" else (None, None)
        return _Spec(
            id=cid,
            kind=kind,
            title=rule.title,
            description=rule.description,
            info=info,
            time_limit_minutes=rule.time_limit_minutes,
            bonus_xp=rule.bonus_xp,
            retry=rule.retry,
            stages=stages,
            period=period,
            starts_at=starts,
            ends_at=ends,
            boss_name=boss_name,
            boss_sprite=boss_sprite,
        )

    async def _current(self, kind: ChallengeKind, language_id: str) -> _Spec:
        return await self._periodic(kind, period_of(kind, utcnow()), language_id)

    async def _by_id(self, cid: str) -> _Spec:
        parsed = parse_id(cid)
        if not parsed:
            raise NotFoundError("Challenge not found.")
        return await self._periodic(*parsed)

    async def _zone(self, user_id: str, course_id: str, boss_id: str) -> _Spec:
        course = await self.learning.get_course(user_id, course_id)
        if course.kind == "framework":
            raise ConflictError("A framework's boss is a quiz on its docs: fight it from the quiz page.")
        zone = next((z for z in await self.learning.course_path(user_id, course_id) if z.boss.id == boss_id), None)
        if not zone:
            raise NotFoundError("Boss not found on this map.")
        info = self._language(course.language)
        boss = zone.boss
        cid = f"zone-{boss.id}"
        stages = await self._stages(info, cid, cid, (ZONE_LEVELS[zone.difficulty],) * boss.stages, ZONE_PICK_TTL)
        return _Spec(
            id=cid,
            kind="zone",
            title=f"{zone.name} boss",
            description=boss.challenge,
            info=info,
            time_limit_minutes=ZONE_MINUTES_PER_ROUND * len(stages),
            bonus_xp=boss.xp_reward,
            retry=True,
            stages=stages,
            boss_name=boss.name,
            boss_sprite=boss.sprite,
            course_id=course_id,
            boss_id=boss.id,
            locked=boss.state == "locked",
            defeated=boss.state == "completed",
        )

    # --- Views -------------------------------------------------------------------------------------------

    @staticmethod
    def _status(spec: _Spec, doc: dict | None, now: datetime) -> str:
        if doc and doc.get("won_at") or spec.defeated:
            return "won"
        if doc and as_utc(doc["deadline"]) > now:
            return "in_progress"
        if spec.ends_at and now >= spec.ends_at:
            return "ended"
        return "timed_out" if doc else "not_started"

    async def _fastest(self, spec: _Spec, user_id: str) -> list[ChallengeRunner]:
        docs = await self.attempts.fastest(spec.id, FASTEST_SHOWN)
        players = {u.id: u for u in await self.users.get_many([d["user_id"] for d in docs])}
        return [
            ChallengeRunner(
                rank=i + 1,
                player_id=p.id,
                username=p.username,
                avatar_color=p.avatar_color,
                avatar_initials=p.avatar_initials,
                seconds=d["seconds"],
                is_you=p.id == user_id,
            )
            for i, d in enumerate(docs)
            if (p := players.get(d["user_id"]))
        ]

    async def _view(
        self, user_id: str, spec: _Spec, doc: dict | None = None, *, fetched: bool = False
    ) -> LiveChallenge:
        if not fetched:
            doc = await self.attempts.get(user_id, spec.id)
        now = utcnow()
        status = self._status(spec, doc, now)
        cleared = (
            set(spec.slugs) if status == "won" else set(doc["cleared"]) if doc and status == "in_progress" else set()
        )
        players, winners = await self.attempts.counts(spec.id)
        return LiveChallenge(
            id=spec.id,
            kind=spec.kind,  # type: ignore[arg-type]
            title=spec.title,
            description=spec.description,
            language=spec.info.id,
            language_name=spec.info.name,
            gradable=self.library.gradable(spec.info.id),
            period=spec.period,
            starts_at=spec.starts_at,
            ends_at=spec.ends_at,
            time_limit_minutes=spec.time_limit_minutes,
            bonus_xp=spec.bonus_xp,
            boss_name=spec.boss_name,
            boss_sprite=spec.boss_sprite,
            course_id=spec.course_id,
            boss_id=spec.boss_id,
            locked=spec.locked,
            stages=[
                ChallengeStage(
                    slug=s.slug,
                    name=s.name,
                    difficulty=difficulty_for(s.difficulty),
                    level=s.difficulty,
                    topics=s.topics,
                    cleared=s.slug in cleared,
                    exercism_url=website_url(spec.info.exercism_track, s.slug),
                )
                for s in spec.stages
            ],
            players=players,
            winners=winners,
            fastest=await self._fastest(spec, user_id),
            me=ChallengeAttempt(
                status=status,  # type: ignore[arg-type]
                started_at=doc["started_at"] if doc else None,
                deadline=doc["deadline"] if doc else None,
                seconds=doc.get("seconds") if doc else None,
                tries=doc.get("tries", 0) if doc else 0,
            ),
            source_url=f"https://github.com/exercism/{spec.info.exercism_track}",
        )

    # --- Playing -------------------------------------------------------------------------------------------

    def _require_gradable(self, spec: _Spec) -> None:
        if not self.library.gradable(spec.info.id):
            raise UnprocessableError(
                f"{spec.info.name} tests can't run on this server yet — solve these on Exercism's online editor."
            )

    async def _start(self, user_id: str, spec: _Spec) -> LiveChallenge:
        self._require_gradable(spec)
        if spec.locked:
            raise ConflictError("Clear every topic in this zone before fighting its boss.")
        now = utcnow()
        doc = await self.attempts.get(user_id, spec.id)
        status = self._status(spec, doc, now)
        deadline = now + timedelta(minutes=spec.time_limit_minutes)
        if status in ("won", "in_progress"):
            return await self._view(user_id, spec, doc, fetched=True)
        if status == "ended":
            raise ConflictError("This challenge has ended — a new one is already live.")
        if doc is None:
            doc = await self.attempts.start(user_id, spec.id, now, deadline)
        elif spec.retry:
            doc = await self.attempts.restart(user_id, spec.id, now, deadline)
        else:
            raise ConflictError("You've had your run at this one. A new challenge starts at 00:00 UTC.")
        return await self._view(user_id, spec, doc, fetched=True)

    async def _submit(self, user_id: str, spec: _Spec, slug: str, files: dict[str, str]) -> ChallengeSubmitResult:
        self._require_gradable(spec)
        if slug not in spec.slugs:
            raise NotFoundError("That exercise isn't part of this challenge.")
        doc = await self.attempts.get(user_id, spec.id)
        if doc is None:
            raise ConflictError("Start the challenge first — that starts your clock.")

        # Grades the code and records the solve like any library exercise (first solve pays its XP).
        result = await self.library.submit(user_id, spec.info.id, slug, files)
        now = utcnow()
        won, bonus = False, 0
        running = doc.get("won_at") is None and as_utc(doc["deadline"]) > now
        current = next((s for s in spec.slugs if s not in doc["cleared"]), None)
        if result.status == "passed" and running and slug == current:
            doc = await self.attempts.clear_stage(user_id, spec.id, slug, now) or doc
            if spec.kind in ("boss", "zone"):
                await self.tracker.record(user_id, "boss_stage_cleared")
            if all(s in doc["cleared"] for s in spec.slugs):
                seconds = max(1, int((now - as_utc(doc["started_at"])).total_seconds()))
                if await self.attempts.mark_won(user_id, spec.id, now, seconds):
                    won, bonus = True, await self._reward(user_id, spec, seconds)
        return ChallengeSubmitResult(
            result=result,
            challenge=await self._view(user_id, spec),
            won=won,
            bonus_xp=bonus,
            balance=await self.wallet.balance(user_id),
        )

    async def _reward(self, user_id: str, spec: _Spec, seconds: int) -> int:
        if spec.kind == "zone":
            assert spec.course_id and spec.boss_id
            return (await self.learning.defeat_boss(user_id, spec.course_id, spec.boss_id)).awarded

        award = await self.wallet.earn(
            user_id,
            spec.bonus_xp,
            f"Won the {spec.info.name} {spec.title}",
            reward_key=f"challenge:{spec.id}",
            activity=f"beat {spec.boss_name}" if spec.boss_name else f"won the {spec.info.name} {spec.title}",
            sprite={"daily": "star", "speed": "lightning", "boss": "trophy"}[spec.kind],
        )
        if award.awarded:
            stats = {"challenges_won": 1}
            if spec.kind == "boss":
                stats["bosses_defeated"] = 1
            if spec.kind == "speed" and seconds <= SPEED_RECORD_SECONDS:
                stats["speed_records"] = 1
            await self.users.inc_stats(user_id, stats)
            await self.tracker.refresh_achievements(user_id)
        return award.awarded

    # --- Public API: rotating challenges -------------------------------------------------------------

    async def board(self, user_id: str, language_id: str) -> list[LiveChallenge]:
        """Today's Daily and Speed challenges and this week's Boss, in one language."""
        specs = await asyncio.gather(*(self._current(kind, language_id) for kind in KINDS))
        return [await self._view(user_id, spec) for spec in specs]

    async def get(self, user_id: str, cid: str) -> LiveChallenge:
        return await self._view(user_id, await self._by_id(cid))

    async def start(self, user_id: str, cid: str) -> LiveChallenge:
        return await self._start(user_id, await self._by_id(cid))

    async def submit(self, user_id: str, cid: str, slug: str, files: dict[str, str]) -> ChallengeSubmitResult:
        return await self._submit(user_id, await self._by_id(cid), slug, files)

    # --- Public API: zone bosses ------------------------------------------------------------------------

    async def zone_boss(self, user_id: str, course_id: str, boss_id: str) -> LiveChallenge:
        return await self._view(user_id, await self._zone(user_id, course_id, boss_id))

    async def start_zone_boss(self, user_id: str, course_id: str, boss_id: str) -> LiveChallenge:
        return await self._start(user_id, await self._zone(user_id, course_id, boss_id))

    async def submit_zone_boss(
        self, user_id: str, course_id: str, boss_id: str, slug: str, files: dict[str, str]
    ) -> ChallengeSubmitResult:
        return await self._submit(user_id, await self._zone(user_id, course_id, boss_id), slug, files)

    async def claim_zone_boss(self, user_id: str, course_id: str, boss_id: str) -> LessonCompletion:
        """Languages this server can't grade: the player solved the rounds on exercism.org, so the gate opens.

        Nothing is verified, so no XP is paid.
        """
        spec = await self._zone(user_id, course_id, boss_id)
        if self.library.gradable(spec.info.id):
            raise ConflictError("Beat this boss by passing its rounds here.")
        return await self.learning.defeat_boss(user_id, course_id, boss_id, award_xp=False)
