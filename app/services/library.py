"""The practice library: live Exercism exercises for all 13 course languages.

Exercises come straight from Exercism's open-source track repositories. Python, JavaScript, TypeScript
and SQL are graded on this server against each exercise's own test suite; for the other languages the
library shows the exercise and sends learners to Exercism's free online editor to run the tests.
"""

import asyncio

from app.core.clock import new_id, utcnow
from app.core.config import Settings
from app.core.errors import NotFoundError, ServiceUnavailableError, UnprocessableError
from app.domain.languages import LANGUAGES, LanguageInfo
from app.integrations.execution import CodeExecutor
from app.integrations.exercism.client import ExercismClient, ExercismUnavailable, website_url
from app.integrations.exercism.runners import run_suite
from app.repositories.player_content import SubmissionRepository
from app.repositories.users import UserRepository
from app.schemas.library import (
    ExerciseDetail,
    ExerciseList,
    ExerciseRunResult,
    ExerciseSummary,
    ExerciseTestResult,
    LibraryLanguage,
)
from app.services.quests import ProgressTracker
from app.services.wallet import WalletService

# Languages whose Exercism test suites this server can run (see app/integrations/exercism/runners.py).
GRADED_HERE = {"python", "javascript", "typescript", "sql"}
SUBMISSION_KIND = "exercism"


def difficulty_for(level: int) -> str:
    """Exercism rates exercises 1–10."""
    return "easy" if level <= 3 else "medium" if level <= 6 else "hard"


def xp_for(level: int) -> int:
    return {"easy": 60, "medium": 120, "hard": 200}[difficulty_for(level)]


class LibraryService:
    def __init__(
        self,
        client: ExercismClient,
        executor: CodeExecutor,
        submissions: SubmissionRepository,
        users: UserRepository,
        wallet: WalletService,
        tracker: ProgressTracker,
        settings: Settings,
    ):
        self.client = client
        self.executor = executor
        self.submissions = submissions
        self.users = users
        self.wallet = wallet
        self.tracker = tracker
        self.settings = settings

    # --- Languages -------------------------------------------------------------------------------

    def _language(self, language_id: str) -> LanguageInfo:
        info = LANGUAGES.get(language_id)
        if not info:
            raise NotFoundError(f"There's no {language_id} track.")
        return info

    def gradable(self, language_id: str) -> bool:
        runtime = "python" if language_id == "sql" else language_id
        return language_id in GRADED_HERE and self.executor.supports(runtime)

    def _view(self, info: LanguageInfo, count: int | None = None, solved: int = 0) -> LibraryLanguage:
        return LibraryLanguage(
            id=info.id,
            name=info.name,
            track=info.exercism_track,
            gradable=self.gradable(info.id),
            exercise_count=count,
            solved=solved,
        )

    async def _solved(self, user_id: str) -> set[str]:
        return await self.submissions.solved_slugs(user_id, SUBMISSION_KIND)

    async def languages(self, user_id: str) -> list[LibraryLanguage]:
        async def count(info: LanguageInfo) -> int | None:
            try:
                return len(await self.client.exercises(info.exercism_track))
            except ExercismUnavailable:
                return None

        infos = list(LANGUAGES.values())
        counts, solved = await asyncio.gather(asyncio.gather(*(count(i) for i in infos)), self._solved(user_id))
        return [
            self._view(info, n, sum(1 for key in solved if key.startswith(f"{info.id}/")))
            for info, n in zip(infos, counts, strict=True)
        ]

    # --- Exercises -------------------------------------------------------------------------------

    async def list_exercises(
        self, user_id: str, language_id: str, *, difficulty: str | None, search: str | None
    ) -> ExerciseList:
        info = self._language(language_id)
        try:
            exercises = await self.client.exercises(info.exercism_track)
        except ExercismUnavailable as exc:
            raise ServiceUnavailableError("Exercism can't be reached right now — try again in a minute.") from exc
        solved = await self._solved(user_id)
        needle = (search or "").strip().lower()
        items = [
            ExerciseSummary(
                slug=e.slug,
                name=e.name,
                difficulty=difficulty_for(e.difficulty),
                level=e.difficulty,
                xp=xp_for(e.difficulty),
                topics=e.topics,
                solved=f"{info.id}/{e.slug}" in solved,
            )
            for e in exercises
            if (not difficulty or difficulty_for(e.difficulty) == difficulty)
            and (not needle or needle in e.name.lower() or any(needle in t for t in e.topics))
        ]
        items.sort(key=lambda e: (e.level, e.name))
        return ExerciseList(
            language=self._view(info, len(exercises), sum(1 for k in solved if k.startswith(f"{info.id}/"))),
            exercises=items,
            source_url=f"https://github.com/exercism/{info.exercism_track}",
        )

    async def _files(self, info: LanguageInfo, slug: str):
        try:
            files = await self.client.exercise(info.exercism_track, slug)
        except ExercismUnavailable as exc:
            raise ServiceUnavailableError("Exercism can't be reached right now — try again in a minute.") from exc
        if not files:
            raise NotFoundError("Exercise not found.")
        return files

    async def _level(self, info: LanguageInfo, slug: str) -> tuple[int, list[str]]:
        summary = next((e for e in await self.client.exercises(info.exercism_track) if e.slug == slug), None)
        return (summary.difficulty, summary.topics) if summary else (1, [])

    async def get(self, user_id: str, language_id: str, slug: str) -> ExerciseDetail:
        info = self._language(language_id)
        files = await self._files(info, slug)
        level, topics = await self._level(info, slug)
        return ExerciseDetail(
            language=self._view(info),
            slug=files.slug,
            name=files.name,
            blurb=files.blurb,
            difficulty=difficulty_for(level),
            level=level,
            xp=xp_for(level),
            topics=topics,
            instructions=files.instructions,
            solution=files.solution,
            tests=files.tests,
            solved=f"{info.id}/{slug}" in await self._solved(user_id),
            exercism_url=website_url(info.exercism_track, slug),
            source=files.source,
            source_url=files.source_url,
        )

    # --- Running -----------------------------------------------------------------------------------

    async def _run(self, language_id: str, slug: str, submitted: dict[str, str]) -> ExerciseRunResult:
        info = self._language(language_id)
        if not self.gradable(language_id):
            raise UnprocessableError(
                f"{info.name} tests can't run on this server yet — solve this one on Exercism's online editor."
            )
        files = await self._files(info, slug)
        # Only the exercise's own solution files can be replaced; the tests always come from Exercism.
        solution = {name: submitted.get(name, starter) for name, starter in files.solution.items()}
        result = await run_suite(
            self.executor,
            language_id,
            solution,
            files.tests,
            files.support,
            timeout_seconds=self.settings.exercise_timeout_seconds,
        )
        passed_count = sum(1 for t in result.tests if t.status == "pass")
        status = "error" if result.error and not result.tests else "passed" if result.passed else "failed"
        return ExerciseRunResult(
            status=status,
            tests=[ExerciseTestResult(name=t.name, status=t.status, message=t.message) for t in result.tests],
            passed_count=passed_count,
            total=len(result.tests),
            stdout=result.stdout,
            error=result.error,
            runtime_ms=result.runtime_ms,
        )

    async def starter_fails(self, language_id: str, slug: str) -> bool:
        """Whether the untouched starter code runs here and fails the tests (so the exercise can be graded)."""
        return (await self._run(language_id, slug, {})).status == "failed"

    async def run(self, language_id: str, slug: str, submitted: dict[str, str]) -> ExerciseRunResult:
        """Runs the tests. Nothing is recorded and no XP is paid."""
        return await self._run(language_id, slug, submitted)

    async def submit(self, user_id: str, language_id: str, slug: str, submitted: dict[str, str]) -> ExerciseRunResult:
        result = await self._run(language_id, slug, submitted)
        passed = result.status == "passed"
        key = f"{language_id}/{slug}"
        if result.status != "error":
            await self.submissions.insert(
                {
                    "_id": new_id(),
                    "user_id": user_id,
                    "kind": SUBMISSION_KIND,
                    "slug": key,
                    "passed": passed,
                    "created_at": utcnow(),
                }
            )
            await self.users.inc_stats(
                user_id, {"submissions_total": 1, **({"submissions_passed": 1} if passed else {})}
            )
        if not passed:
            result.balance = await self.wallet.balance(user_id)
            return result

        info = self._language(language_id)
        level, _ = await self._level(info, slug)
        name = (await self._files(info, slug)).name
        award = await self.wallet.earn(
            user_id,
            xp_for(level),
            f"Solved {name} ({info.name})",
            reward_key=f"exercism:{key}",
            activity=f"solved {name} in {info.name}",
            sprite="database" if language_id == "sql" else "terminal",
        )
        result.awarded_xp, result.balance = award.awarded, award.balance
        if award.awarded:
            await self.users.inc_stats(user_id, {"sql_solved" if language_id == "sql" else "code_solved": 1})
            await self.tracker.record(user_id, "sql_solved" if language_id == "sql" else "problem_solved")
        return result
