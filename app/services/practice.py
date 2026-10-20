"""Coding problems: real execution against test cases, rewards on first solve, duel timing."""

import json
from typing import Any

from app.core.clock import new_id, utcnow
from app.core.errors import NotFoundError
from app.domain.code_review import review
from app.integrations.execution import CodeExecutor
from app.integrations.execution.base import ExecutionUnavailable
from app.integrations.execution.harness import build_program, parse_case_args, parse_output
from app.repositories.catalog import ProblemRepository
from app.repositories.player_content import SubmissionRepository
from app.repositories.users import UserRepository
from app.schemas.practice import (
    Problem,
    ProblemSummary,
    RunCodeRequest,
    SubmissionResult,
    SubmitCodeRequest,
    TestCase,
    TestResult,
)
from app.services.quests import ProgressTracker
from app.services.social import DuelService
from app.services.wallet import WalletService


def _normalise(value: Any, unordered: bool) -> Any:
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, list):
        items = [_normalise(v, unordered) for v in value]
        return sorted(items, key=json.dumps) if unordered else items
    return value


def _show(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"))


class PracticeService:
    def __init__(
        self,
        problems: ProblemRepository,
        submissions: SubmissionRepository,
        users: UserRepository,
        executor: CodeExecutor,
        wallet: WalletService,
        tracker: ProgressTracker,
        duels: DuelService,
    ):
        self.problems = problems
        self.submissions = submissions
        self.users = users
        self.executor = executor
        self.wallet = wallet
        self.tracker = tracker
        self.duels = duels

    async def list_problems(
        self, user_id: str, *, difficulty: str | None, tag: str | None, search: str | None
    ) -> list[ProblemSummary]:
        solved = await self.submissions.solved_slugs(user_id, "code")
        items = []
        for p in await self.problems.list():
            if difficulty and p.difficulty != difficulty:
                continue
            if tag and tag.lower() not in (t.lower() for t in p.tags):
                continue
            if search and search.lower() not in p.title.lower():
                continue
            fields = p.model_dump(include=set(ProblemSummary.model_fields) - {"solved"})
            items.append(ProblemSummary(**fields, solved=p.slug in solved))
        return items

    async def _problem(self, slug: str) -> Problem:
        problem = await self.problems.by_slug(slug)
        if not problem:
            raise NotFoundError("Problem not found.")
        return problem

    async def get(self, user_id: str, slug: str) -> Problem:
        problem = await self._problem(slug)
        solved = slug in await self.submissions.solved_slugs(user_id, "code")
        return problem.model_copy(
            update={"test_cases": [t for t in problem.test_cases if not t.hidden], "solved": solved}
        )

    async def _execute(self, problem: Problem, body: RunCodeRequest, cases: list[TestCase]) -> SubmissionResult:
        entry = problem.entrypoints.get(body.language)
        if not entry or not self.executor.supports(body.language):
            return SubmissionResult(
                status="error",
                test_results=[],
                error=f"Running {body.language} isn't supported yet — switch to Python or JavaScript to test your solution.",
            )
        program = build_program(body.language, body.code, entry, [parse_case_args(c.input) for c in cases])
        try:
            output = await self.executor.execute(body.language, program)
        except ExecutionUnavailable as exc:
            return SubmissionResult(status="error", test_results=[], error=str(exc))

        stdout, outcomes = parse_output(output.stdout)
        if output.timed_out:
            return SubmissionResult(
                status="error",
                runtime_ms=output.duration_ms,
                test_results=[],
                stdout=stdout,
                error="Time limit exceeded — look for an infinite loop.",
            )
        if outcomes is None:
            return SubmissionResult(
                status="error",
                runtime_ms=output.duration_ms,
                test_results=[],
                stdout=stdout,
                error=output.stderr.strip() or "Your code exited without running the tests.",
            )

        results = []
        for case, outcome in zip(cases, outcomes, strict=False):
            expected = json.loads(case.expected_output)
            passed = outcome.ok and _normalise(outcome.value, problem.unordered_output) == _normalise(
                expected, problem.unordered_output
            )
            results.append(
                TestResult(
                    id=case.id,
                    passed=passed,
                    input="hidden" if case.hidden else case.input,
                    expected_output="hidden" if case.hidden else case.expected_output,
                    received_output=_show(outcome.value) if outcome.ok else "Error",
                    error=outcome.error,
                )
            )
        all_passed = len(results) == len(cases) and all(r.passed for r in results)
        failure = next((r for r in results if not r.passed), None)
        explanation = None
        if failure:
            explanation = (
                f"Your function raised {failure.error}."
                if failure.error
                else f"For input {failure.input} the expected output is {failure.expected_output}, but your code returned {failure.received_output}."
            )
        return SubmissionResult(
            status="passed" if all_passed else "failed",
            runtime_ms=output.duration_ms,
            test_results=results,
            stdout=stdout,
            ai_failure_explanation=explanation,
        )

    async def run(self, slug: str, body: RunCodeRequest) -> SubmissionResult:
        """Runs the visible test cases only. No reward, nothing recorded."""
        problem = await self._problem(slug)
        return await self._execute(problem, body, [t for t in problem.test_cases if not t.hidden])

    async def submit(self, user_id: str, slug: str, body: SubmitCodeRequest) -> SubmissionResult:
        problem = await self._problem(slug)
        result = await self._execute(problem, body, problem.test_cases)
        passed = result.status == "passed"
        if result.status != "error":
            await self.submissions.insert(
                {
                    "_id": new_id(),
                    "user_id": user_id,
                    "kind": "code",
                    "slug": slug,
                    "language": body.language,
                    "passed": passed,
                    "created_at": utcnow(),
                }
            )
            await self.users.inc_stats(
                user_id, {"submissions_total": 1, **({"submissions_passed": 1} if passed else {})}
            )

        if passed:
            result.ai_review = review(body.code, body.language, problem.entrypoints[body.language])
            award = await self.wallet.earn(
                user_id,
                problem.xp,
                f"Solved {problem.title}",
                reward_key=f"code:{slug}",
                activity=f"solved {problem.title}",
                sprite="terminal",
            )
            result.awarded_xp, result.balance = award.awarded, award.balance
            if award.awarded:
                timed = {"solve_seconds_total": body.elapsed_seconds, "solves_timed": 1} if body.elapsed_seconds else {}
                await self.users.inc_stats(user_id, {"code_solved": 1, **timed})
                await self.tracker.record(user_id, "problem_solved")
            if body.duel_id:
                result.duel = await self.duels.record_solve(user_id, body.duel_id, slug)
        else:
            result.balance = await self.wallet.balance(user_id)
        return result
