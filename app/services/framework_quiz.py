"""Practice and challenges for framework courses.

Frameworks can't be graded the way language exercises are (there is no React or FastAPI to run), so they
are practised and fought with quizzes built from the docs themselves (domain/framework_quiz.py):

- Practice: a quiz on one lesson, untimed, any number of tries. The first pass pays XP.
- Daily: a mixed quiz across a whole framework, timed, one run per UTC day, with a bonus.
- Zone boss: a quiz on the zone's topics, timed, retryable (every run draws fresh questions). Passing it
  defeats the boss and opens the next zone, exactly like beating the exercise-based boss of a language course.

Questions are generated once and kept for the length of a run, so grading checks what the learner was shown.
"""

import asyncio
from dataclasses import asdict, dataclass, replace
from datetime import datetime, time, timedelta

from app.core.clock import as_utc, today, utcnow
from app.core.errors import ConflictError, NotFoundError, UnprocessableError
from app.domain.docs_courses import parse_id as parse_framework_id
from app.domain.framework_quiz import Question, make_questions
from app.repositories.exercism_cache import ExercismCacheRepository
from app.repositories.framework_quiz import QuizAttemptRepository
from app.schemas.framework_quiz import (
    FrameworkQuiz,
    FrameworkSummary,
    PracticeTopic,
    QuestionResult,
    QuizQuestionOut,
    QuizResult,
    QuizStatus,
    QuizSubmission,
)
from app.schemas.learning import Course, LessonCompletion, PathZone
from app.services.learning import LearningService
from app.services.quests import ProgressTracker
from app.services.wallet import WalletService

MIN_QUESTIONS = 3
PRACTICE_QUESTIONS, PRACTICE_PASS, XP_PER_QUESTION = 6, 70, 8
DAILY_QUESTIONS, DAILY_PASS, DAILY_MINUTES, DAILY_BONUS, DAILY_TOPICS = 5, 70, 8, 100, 8
ZONE_QUESTIONS, ZONE_PASS, ZONE_MINUTES = 6, 75, 12
PREFIX = "fwq-"
QUESTION_TTL = 12 * 60 * 60
DAILY_TTL = 2 * 24 * 60 * 60


@dataclass
class _Spec:
    id: str
    kind: str
    course: Course
    title: str
    description: str
    question_count: int
    pass_percent: int
    xp: int
    minutes: int | None
    retry: bool
    lesson_id: str | None = None
    zone: PathZone | None = None
    ends_at: datetime | None = None
    locked: bool = False
    defeated: bool = False


def _next_midnight(now: datetime) -> datetime:
    return datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=now.tzinfo)


class FrameworkQuizService:
    def __init__(
        self,
        learning: LearningService,
        attempts: QuizAttemptRepository,
        cache: ExercismCacheRepository,
        wallet: WalletService,
        tracker: ProgressTracker,
        users,
    ):
        self.learning = learning
        self.attempts = attempts
        self.cache = cache
        self.wallet = wallet
        self.tracker = tracker
        self.users = users

    # --- Finding what to quiz on ----------------------------------------------------------------------------

    async def _framework(self, user_id: str, course_id: str) -> tuple[Course, list[PathZone]]:
        course = await self.learning.get_course(user_id, course_id)
        if course.kind != "framework":
            raise NotFoundError("That isn't a framework course.")
        return course, await self.learning.course_path(user_id, course_id)

    async def _pages(self, lesson_ids: list[str]) -> dict[str, str]:
        """{lesson id: Markdown}; a page that can't be loaded right now is simply left out."""

        async def one(lesson_id: str) -> tuple[str, str | None]:
            try:
                return lesson_id, (await self.learning.lesson_content(lesson_id)).live_content
            except Exception:  # noqa: BLE001 — one unreachable page must not sink the quiz
                return lesson_id, None

        return {lid: text for lid, text in await asyncio.gather(*(one(i) for i in lesson_ids)) if text}

    async def _spec(self, user_id: str, quiz_id: str) -> _Spec:
        if not quiz_id.startswith(PREFIX):
            raise NotFoundError("Quiz not found.")
        kind, _, rest = quiz_id.removeprefix(PREFIX).partition("-")
        if kind == "practice":
            parsed = parse_framework_id(rest)
            if not parsed or not parsed[1]:
                raise NotFoundError("Quiz not found.")
            course, zones = await self._framework(user_id, f"fw-{parsed[0]}")
            node = next((n for z in zones for n in z.nodes if n.id == rest), None)
            if not node:
                raise NotFoundError("Quiz not found.")
            return _Spec(
                id=quiz_id,
                kind="practice",
                course=course,
                title=f"{node.title} quiz",
                description=f"Fill in the key terms from the {course.title} lesson “{node.title}”.",
                question_count=PRACTICE_QUESTIONS,
                pass_percent=PRACTICE_PASS,
                xp=XP_PER_QUESTION * PRACTICE_QUESTIONS,
                minutes=None,
                retry=True,
                lesson_id=rest,
                zone=next(z for z in zones if node in z.nodes),
            )
        if kind == "zone":
            parsed = parse_framework_id(rest)
            if not parsed:
                raise NotFoundError("Quiz not found.")
            course, zones = await self._framework(user_id, f"fw-{parsed[0]}")
            zone = next((z for z in zones if z.boss.id == rest), None)
            if not zone:
                raise NotFoundError("Boss not found on this map.")
            return _Spec(
                id=quiz_id,
                kind="zone",
                course=course,
                title=f"{zone.name} boss",
                description=f"Pass a {ZONE_QUESTIONS}-question quiz on {zone.name} to defeat {zone.boss.name} and open the next zone.",
                question_count=ZONE_QUESTIONS,
                pass_percent=ZONE_PASS,
                xp=zone.boss.xp_reward,
                minutes=ZONE_MINUTES,
                retry=True,
                zone=zone,
                locked=zone.boss.state == "locked",
                defeated=zone.boss.state == "completed",
            )
        if kind == "daily":
            day, _, course_id = rest.partition("-")
            now = utcnow()
            if day != today().strftime("%Y%m%d"):
                raise ConflictError("That daily quiz has ended — today's is live.")
            course, zones = await self._framework(user_id, course_id)
            return _Spec(
                id=quiz_id,
                kind="daily",
                course=course,
                title=f"{course.title} daily quiz",
                description=f"{DAILY_QUESTIONS} questions across {course.title}, the same for every player today. One run, {DAILY_MINUTES} minutes.",
                question_count=DAILY_QUESTIONS,
                pass_percent=DAILY_PASS,
                xp=DAILY_BONUS,
                minutes=DAILY_MINUTES,
                retry=False,
                zone=None,
                ends_at=_next_midnight(now),
            )
        raise NotFoundError("Quiz not found.")

    # --- Questions --------------------------------------------------------------------------------------------

    async def _questions(self, user_id: str, spec: _Spec, tries: int) -> list[Question]:
        """The quiz's questions, generated once and remembered while they're in play."""
        key = f"fwq:{spec.id}:{tries if spec.kind == 'zone' else 0}"
        cached = await self.cache.get(key)
        if cached is not None:
            return [Question(**q) for q in cached]

        _, zones = await self._framework(user_id, spec.course.id)
        lesson_ids_of = lambda zone: [n.id for n in zone.nodes]  # noqa: E731
        if spec.kind == "practice":
            assert spec.lesson_id and spec.zone
            pages = await self._pages(sorted({spec.lesson_id, *lesson_ids_of(spec.zone)}))
            own = {spec.lesson_id: pages[spec.lesson_id]} if spec.lesson_id in pages else {}
            questions = make_questions(
                own, seed=f"practice:{spec.lesson_id}", count=spec.question_count, per_page=spec.question_count, pool_pages=pages
            )
            if len(questions) < spec.question_count:  # a short page: top up from its neighbours in the zone
                neighbours = {k: v for k, v in pages.items() if k != spec.lesson_id}
                questions += make_questions(
                    neighbours,
                    seed=f"practice-extra:{spec.lesson_id}",
                    count=spec.question_count - len(questions),
                    per_page=2,
                    pool_pages=pages,
                )
            ttl = QUESTION_TTL
        elif spec.kind == "zone":
            assert spec.zone
            zone_ids = lesson_ids_of(spec.zone)
            pages = await self._pages(zone_ids)
            seed = f"zone:{spec.id}:{tries}"
            questions = make_questions(pages, seed=seed, count=spec.question_count, per_page=2)
            if len(questions) < spec.question_count:  # thin zone: fill from the rest of the framework
                rest = [n.id for z in zones for n in z.nodes if n.id not in zone_ids]
                more = await self._pages(sorted(rest, key=lambda lid: hash_key(seed, lid))[:DAILY_TOPICS])
                questions += make_questions(
                    more, seed=seed + ":fill", count=spec.question_count - len(questions), per_page=1, pool_pages={**pages, **more}
                )
            ttl = QUESTION_TTL
        else:
            every = [n.id for z in zones for n in z.nodes]
            seed = f"daily:{spec.id}"
            chosen = sorted(every, key=lambda lid: hash_key(seed, lid))[:DAILY_TOPICS]
            pages = await self._pages(chosen)
            questions = make_questions(pages, seed=seed, count=spec.question_count, per_page=1)
            ttl = DAILY_TTL
        # Several calls above number their questions from 1; make the ids unique across the quiz.
        questions = [replace(q, id=f"q{i + 1}-{q.id.split('-', 1)[1]}") for i, q in enumerate(questions)]
        if questions:
            await self.cache.put(key, [asdict(q) for q in questions], ttl_seconds=ttl)
        return questions

    # --- Views ----------------------------------------------------------------------------------------------------

    @staticmethod
    def _status(spec: _Spec, doc: dict | None, now: datetime) -> QuizStatus:
        if spec.defeated or (doc and doc.get("passed_at")):
            return "passed"
        if not doc or (spec.minutes is not None and not doc.get("started_at")):
            return "not_started"
        if spec.minutes is None:
            return "not_started"
        if not doc.get("finished_at") and as_utc(doc["deadline"]) > now:
            return "in_progress"
        return "failed" if doc.get("finished_at") else "timed_out"

    async def _view(
        self, user_id: str, spec: _Spec, doc: dict | None = None, *, fetched: bool = False, questions: bool = True
    ) -> FrameworkQuiz:
        if not fetched:
            doc = await self.attempts.get(user_id, spec.id)
        now = utcnow()
        status = self._status(spec, doc, now)
        tries = (doc or {}).get("tries", 0)
        shown = None
        available = True
        if questions and not spec.locked and (status != "passed" or spec.kind == "practice"):
            generated = await self._questions(user_id, spec, tries)
            available = len(generated) >= MIN_QUESTIONS
            if available and (spec.kind == "practice" or status == "in_progress"):
                shown = [QuizQuestionOut(id=q.id, prompt=q.prompt, options=q.options, lesson_id=q.lesson_id) for q in generated]
        return FrameworkQuiz(
            id=spec.id,
            kind=spec.kind,  # type: ignore[arg-type]
            title=spec.title,
            description=spec.description,
            course_id=spec.course.id,
            course_title=spec.course.title,
            language=spec.course.language,
            lesson_id=spec.lesson_id,
            boss_id=spec.zone.boss.id if spec.kind == "zone" and spec.zone else None,
            boss_name=spec.zone.boss.name if spec.kind == "zone" and spec.zone else None,
            boss_sprite=spec.zone.boss.sprite if spec.kind == "zone" and spec.zone else None,
            question_count=len(shown) if shown else spec.question_count,
            pass_percent=spec.pass_percent,
            time_limit_minutes=spec.minutes,
            xp=spec.xp,
            available=available,
            locked=spec.locked,
            defeated=spec.defeated,
            retry=spec.retry,
            status=status,
            best_percent=(doc or {}).get("best_percent"),
            tries=tries,
            deadline=doc.get("deadline") if doc and status == "in_progress" else None,
            questions=shown,
            ends_at=spec.ends_at,
        )

    # --- Public API: lists ------------------------------------------------------------------------------------------

    async def frameworks(self, user_id: str) -> list[FrameworkSummary]:
        courses = [c for c in await self.learning.list_courses(user_id) if c.kind == "framework"]
        solved = await self.attempts.solved_counts(user_id)
        return [
            FrameworkSummary(
                course_id=c.id,
                title=c.title,
                language=c.language,
                topics=sum(m.lessons_count for m in c.modules),
                solved=solved.get(c.id, 0),
                progress_percent=c.progress_percent,
            )
            for c in courses
        ]

    async def practice_topics(self, user_id: str, course_id: str) -> list[PracticeTopic]:
        _, zones = await self._framework(user_id, course_id)
        done = await self.attempts.practice_for_course(user_id, course_id)
        return [
            PracticeTopic(
                lesson_id=n.id,
                title=n.title,
                section=z.name,
                solved=bool(done.get(n.id, {}).get("passed_at")),
                best_percent=done.get(n.id, {}).get("best_percent"),
            )
            for z in zones
            for n in z.nodes
        ]

    async def challenges(self, user_id: str, course_id: str) -> list[FrameworkQuiz]:
        """Today's daily quiz and every zone boss of one framework (questions appear once a run is started)."""
        _, zones = await self._framework(user_id, course_id)
        ids = [f"{PREFIX}daily-{today().strftime('%Y%m%d')}-{course_id}", *(f"{PREFIX}zone-{z.boss.id}" for z in zones)]
        specs = [await self._spec(user_id, quiz_id) for quiz_id in ids]
        return [await self._view(user_id, spec, questions=False) for spec in specs]

    # --- Public API: playing ---------------------------------------------------------------------------------------

    async def get(self, user_id: str, quiz_id: str) -> FrameworkQuiz:
        return await self._view(user_id, await self._spec(user_id, quiz_id))

    async def start(self, user_id: str, quiz_id: str) -> FrameworkQuiz:
        spec = await self._spec(user_id, quiz_id)
        if spec.minutes is None:
            raise UnprocessableError("Practice quizzes have no clock: just answer them.")
        if spec.locked:
            raise ConflictError("Clear every topic in this zone before fighting its boss.")
        doc = await self.attempts.get(user_id, quiz_id)
        now = utcnow()
        status = self._status(spec, doc, now)
        if status in ("in_progress", "passed"):
            return await self._view(user_id, spec, doc, fetched=True)
        if status != "not_started" and not spec.retry:
            raise ConflictError("You've had your run at this one. A new daily quiz starts at 00:00 UTC.")
        deadline = now + timedelta(minutes=spec.minutes)
        doc = await self.attempts.start(
            user_id, quiz_id, course_id=spec.course.id, kind=spec.kind, now=now, deadline=deadline
        )
        if len(await self._questions(user_id, spec, doc.get("tries", 1))) < MIN_QUESTIONS:
            await self.attempts.mark_timed_out(user_id, quiz_id, now)
            raise UnprocessableError("These lessons don't have enough material to quiz on yet.")
        return await self._view(user_id, spec, doc, fetched=True)

    async def claim(self, user_id: str, quiz_id: str) -> LessonCompletion:
        """A zone boss whose docs have too little to quiz on opens the next zone without a fight (no XP)."""
        spec = await self._spec(user_id, quiz_id)
        if spec.kind != "zone" or not spec.zone:
            raise UnprocessableError("Only a zone boss can be claimed.")
        if spec.locked:
            raise ConflictError("Clear every topic in this zone before fighting its boss.")
        doc = await self.attempts.get(user_id, quiz_id)
        if len(await self._questions(user_id, spec, (doc or {}).get("tries", 0))) >= MIN_QUESTIONS:
            raise ConflictError("Beat this boss by passing its quiz.")
        return await self.learning.defeat_boss(user_id, spec.course.id, spec.zone.boss.id, award_xp=False)

    async def submit(self, user_id: str, quiz_id: str, submission: QuizSubmission) -> QuizResult:
        spec = await self._spec(user_id, quiz_id)
        doc = await self.attempts.get(user_id, quiz_id)
        now = utcnow()
        status = self._status(spec, doc, now)
        timed = spec.minutes is not None
        if timed:
            if doc is None or not doc.get("started_at"):
                raise ConflictError("Start the quiz first — that starts your clock.")
            if status == "timed_out":
                await self.attempts.mark_timed_out(user_id, quiz_id, now)
                raise ConflictError("Time's up — your clock ran out before the answers came in.")
            if status != "in_progress":
                raise ConflictError("This run is already over." if status != "passed" else "You already beat this one.")
        tries = (doc or {}).get("tries", 0)
        questions = await self._questions(user_id, spec, tries)
        if len(questions) < MIN_QUESTIONS:
            raise UnprocessableError("These lessons don't have enough material to quiz on yet.")

        chosen = {a.question_id: a.option_index for a in submission.answers}
        results = [
            QuestionResult(
                question_id=q.id,
                correct=chosen.get(q.id) == q.answer,
                chosen=chosen.get(q.id),
                correct_index=q.answer,
                explanation=q.explanation,
                lesson_id=q.lesson_id,
            )
            for q in questions
        ]
        correct = sum(1 for r in results if r.correct)
        percent = round(100 * correct / len(questions))
        passed = percent >= spec.pass_percent
        seconds = max(1, int((now - as_utc(doc["started_at"])).total_seconds())) if timed and doc else None
        first_pass = await self.attempts.finish(
            user_id,
            quiz_id,
            course_id=spec.course.id,
            kind=spec.kind,
            lesson_id=spec.lesson_id,
            percent=percent,
            passed=passed,
            now=now,
            seconds=seconds,
        )
        awarded = await self._reward(user_id, spec, len(questions)) if first_pass else 0
        return QuizResult(
            quiz=await self._view(user_id, spec, questions=False),
            correct=correct,
            total=len(questions),
            percent=percent,
            passed=passed,
            results=results,
            awarded_xp=awarded,
            balance=await self.wallet.balance(user_id),
        )

    async def _reward(self, user_id: str, spec: _Spec, total: int) -> int:
        if spec.kind == "zone":
            assert spec.zone
            return (await self.learning.defeat_boss(user_id, spec.course.id, spec.zone.boss.id)).awarded
        if spec.kind == "practice":
            award = await self.wallet.earn(
                user_id,
                XP_PER_QUESTION * total,
                f"Quiz: {spec.title}",
                reward_key=f"fwquiz:{spec.lesson_id}",
                activity=f"passed the {spec.title}",
                sprite="scroll",
            )
            if award.awarded:
                await self.tracker.record(user_id, "problem_solved")
            return award.awarded
        award = await self.wallet.earn(
            user_id,
            spec.xp,
            f"Won the {spec.title}",
            reward_key=f"fwquiz:{spec.id}",
            activity=f"won the {spec.title}",
            sprite="star",
        )
        if award.awarded:
            await self.users.inc_stats(user_id, {"challenges_won": 1})
            await self.tracker.refresh_achievements(user_id)
        return award.awarded


def hash_key(seed: str, value: str) -> str:
    """A stable, seed-dependent ordering key."""
    import hashlib

    return hashlib.sha256(f"{seed}|{value}".encode()).hexdigest()
