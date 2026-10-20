"""SQL practice: real queries against an in-memory SQLite copy of the practice tables, graded by result."""

import re

from app.core.clock import new_id, utcnow
from app.core.errors import NotFoundError
from app.integrations.sql_sandbox import SqlExecutionError, SqlRun, run_query
from app.repositories.catalog import SqlProblemRepository, SqlTableRepository
from app.repositories.player_content import SubmissionRepository
from app.repositories.users import UserRepository
from app.schemas.sql import GradeResult, QueryResult, SqlProblem, SqlProblemSummary, SqlRunResponse, SqlTable, SqlValue
from app.services.quests import ProgressTracker
from app.services.wallet import WalletService


def _cell(value: SqlValue) -> SqlValue:
    if isinstance(value, float):
        rounded = round(value, 2)
        return int(rounded) if rounded.is_integer() else rounded
    if isinstance(value, str):
        return value.strip()
    return value


def _normalise_query(query: str) -> str:
    return f" {re.sub(r'\s+', ' ', re.sub(r'--.*$', '', query.lower(), flags=re.M))} "


def grade(run: SqlRun, problem: SqlProblem, query: str) -> GradeResult:
    """Compares the query's actual result with the expected one: same columns, same rows (in order if asked)."""
    missing = [c.hint for c in problem.required_clauses if c.fragment not in _normalise_query(query)]
    columns = [c.lower() for c in run.columns]
    expected_columns = [c.lower() for c in problem.expected_columns]
    if sorted(columns) != sorted(expected_columns):
        return GradeResult(
            passed=False,
            missing_hints=missing,
            message=f"Return exactly these columns: {', '.join(problem.expected_columns)} (you returned {', '.join(run.columns) or 'none'}).",
        )

    def as_tuple(row: dict) -> tuple:
        lowered = {k.lower(): v for k, v in row.items()}
        return tuple(_cell(lowered.get(c)) for c in expected_columns)

    actual = [as_tuple(r) for r in run.rows]
    expected = [as_tuple(r) for r in problem.expected_rows]
    if not problem.ordered:
        actual, expected = sorted(actual, key=repr), sorted(expected, key=repr)
    if actual == expected:
        return GradeResult(passed=True, missing_hints=[])
    if len(actual) != len(expected):
        message = f"Expected {len(expected)} rows but your query returned {len(actual)}."
    elif sorted(actual, key=repr) == sorted(expected, key=repr):
        message = "Right rows, wrong order — check your ORDER BY."
    else:
        message = "Some values don't match the expected result."
    return GradeResult(passed=False, missing_hints=missing, message=message)


def _result(run: SqlRun) -> QueryResult:
    return QueryResult(columns=run.columns, rows=run.rows, execution_ms=run.execution_ms, truncated=run.truncated)


class SqlService:
    def __init__(
        self,
        tables: SqlTableRepository,
        problems: SqlProblemRepository,
        submissions: SubmissionRepository,
        users: UserRepository,
        wallet: WalletService,
        tracker: ProgressTracker,
    ):
        self.tables = tables
        self.problems = problems
        self.submissions = submissions
        self.users = users
        self.wallet = wallet
        self.tracker = tracker

    async def list_tables(self) -> list[SqlTable]:
        return await self.tables.list()

    async def query(self, query: str) -> SqlRunResponse:
        try:
            run = await run_query(query, await self.tables.list())
        except SqlExecutionError as exc:
            return SqlRunResponse(result=None, error=str(exc))
        return SqlRunResponse(result=_result(run))

    async def list_problems(self, user_id: str) -> list[SqlProblemSummary]:
        solved = await self.submissions.solved_slugs(user_id, "sql")
        return [
            SqlProblemSummary(
                **p.model_dump(include=set(SqlProblemSummary.model_fields) - {"solved"}), solved=p.slug in solved
            )
            for p in await self.problems.list()
        ]

    async def _problem(self, slug: str) -> SqlProblem:
        problem = await self.problems.by_slug(slug)
        if not problem:
            raise NotFoundError("SQL problem not found.")
        return problem

    async def get_problem(self, user_id: str, slug: str) -> SqlProblem:
        problem = await self._problem(slug)
        return problem.model_copy(update={"solved": slug in await self.submissions.solved_slugs(user_id, "sql")})

    async def _grade(self, slug: str, query: str) -> tuple[SqlProblem, SqlRunResponse]:
        problem = await self._problem(slug)
        try:
            run = await run_query(query, await self.tables.list())
        except SqlExecutionError as exc:
            missing = [c.hint for c in problem.required_clauses if c.fragment not in _normalise_query(query)]
            return problem, SqlRunResponse(
                result=None, error=str(exc), grade=GradeResult(passed=False, missing_hints=missing)
            )
        return problem, SqlRunResponse(result=_result(run), grade=grade(run, problem, query))

    async def run_problem(self, slug: str, query: str) -> SqlRunResponse:
        return (await self._grade(slug, query))[1]

    async def submit_problem(self, user_id: str, slug: str, query: str) -> SqlRunResponse:
        problem, response = await self._grade(slug, query)
        passed = bool(response.grade and response.grade.passed)
        await self.submissions.insert(
            {"_id": new_id(), "user_id": user_id, "kind": "sql", "slug": slug, "passed": passed, "created_at": utcnow()}
        )
        await self.users.inc_stats(user_id, {"submissions_total": 1, **({"submissions_passed": 1} if passed else {})})
        if passed:
            award = await self.wallet.earn(
                user_id,
                problem.xp,
                f"Solved {problem.title}",
                reward_key=f"sql:{slug}",
                activity=f"solved {problem.title}",
                sprite="database",
            )
            response.awarded_xp, response.balance = award.awarded, award.balance
            if award.awarded:
                await self.users.inc_stats(user_id, {"sql_solved": 1})
                await self.tracker.record(user_id, "sql_solved")
            if response.grade:
                response.grade.message = problem.success_note
        else:
            response.balance = await self.wallet.balance(user_id)
        return response
