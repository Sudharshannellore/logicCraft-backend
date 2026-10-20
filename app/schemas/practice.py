from typing import Literal

from pydantic import Field

from app.schemas.common import CamelModel, Difficulty, Language, XpBalance


class Example(CamelModel):
    input: str
    output: str
    explanation: str | None = None


class TestCase(CamelModel):
    id: str
    # Arguments as written in a call, e.g. `[2,7,11,15], 9` — parsed as a JSON array of arguments.
    input: str
    # Expected return value as JSON, e.g. `[0,1]`.
    expected_output: str
    # Hidden cases run on Submit only and are never sent to the client.
    hidden: bool = False


class Problem(CamelModel):
    id: str
    title: str
    slug: str
    difficulty: Difficulty
    xp: int
    acceptance_rate: int
    tags: list[str]
    description: str
    examples: list[Example]
    constraints: list[str]
    hints: list[str]
    starter_code: dict[Language, str]
    # Function the grader calls, per language, e.g. {"python": "two_sum", "javascript": "twoSum"}.
    entrypoints: dict[Language, str]
    # True when any correct answer may list items in a different order (compared sorted).
    unordered_output: bool = False
    test_cases: list[TestCase]
    solved: bool = False


class ProblemSummary(CamelModel):
    id: str
    title: str
    slug: str
    difficulty: Difficulty
    xp: int
    acceptance_rate: int
    tags: list[str]
    solved: bool = False


class TestResult(CamelModel):
    id: str
    passed: bool
    input: str
    expected_output: str
    received_output: str
    error: str | None = None


class AiReview(CamelModel):
    correct: bool
    time_complexity: str
    space_complexity: str
    code_quality: int
    recommendation: str


class SubmissionResult(CamelModel):
    status: Literal["running", "passed", "failed", "error"]
    runtime_ms: int | None = None
    memory_mb: int | None = None
    test_results: list[TestResult]
    stdout: str = ""
    error: str | None = None
    ai_review: AiReview | None = None
    ai_failure_explanation: str | None = None
    # Set on Submit only.
    awarded_xp: int | None = None
    balance: XpBalance | None = None
    duel: "DuelView | None" = None


class RunCodeRequest(CamelModel):
    language: Language
    code: str = Field(max_length=50_000)


class SubmitCodeRequest(RunCodeRequest):
    # Board timer, used for the profile's average solve time.
    elapsed_seconds: int | None = Field(default=None, ge=0, le=24 * 3600)
    # When the board was opened for a friend duel; the server times it.
    duel_id: str | None = None


from app.schemas.social import DuelView  # noqa: E402 — resolves the forward reference above

SubmissionResult.model_rebuild()
