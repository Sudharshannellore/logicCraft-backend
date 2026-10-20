from pydantic import Field

from app.schemas.common import CamelModel, Difficulty, XpBalance

SqlValue = str | int | float | None


class SqlColumn(CamelModel):
    name: str
    type: str


class SqlTable(CamelModel):
    name: str
    columns: list[SqlColumn]
    rows: list[dict[str, SqlValue]]


class RequiredClause(CamelModel):
    fragment: str
    hint: str


class SqlProblem(CamelModel):
    id: str
    title: str
    slug: str
    difficulty: Difficulty
    xp: int
    acceptance_rate: int
    tags: list[str]
    description: str
    tables_used: list[str]
    starter_query: str
    hints: list[str]
    # Used for feedback when a query's result is wrong: which pieces it's probably missing.
    required_clauses: list[RequiredClause]
    expected_columns: list[str]
    expected_rows: list[dict[str, SqlValue]]
    # Row order matters (the problem asks for ORDER BY).
    ordered: bool = False
    success_note: str
    solved: bool = False


class SqlProblemSummary(CamelModel):
    id: str
    title: str
    slug: str
    difficulty: Difficulty
    xp: int
    acceptance_rate: int
    tags: list[str]
    solved: bool = False


class SqlQueryRequest(CamelModel):
    query: str = Field(min_length=1, max_length=10_000)


class QueryResult(CamelModel):
    columns: list[str]
    rows: list[dict[str, SqlValue]]
    execution_ms: int
    truncated: bool = False


class GradeResult(CamelModel):
    passed: bool
    missing_hints: list[str]
    message: str | None = None


class SqlRunResponse(CamelModel):
    result: QueryResult | None
    error: str | None = None
    grade: GradeResult | None = None
    awarded_xp: int | None = None
    balance: XpBalance | None = None
