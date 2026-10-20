"""The practice library: live exercises from Exercism for every course language."""

from typing import Literal

from pydantic import Field

from app.schemas.common import CamelModel, Difficulty, XpBalance

TestStatus = Literal["pass", "fail", "error"]


class LibraryLanguage(CamelModel):
    id: str
    name: str
    track: str
    # True when this server can run the exercise tests; otherwise learners solve on exercism.org.
    gradable: bool
    exercise_count: int | None = None
    solved: int = 0


class ExerciseSummary(CamelModel):
    slug: str
    name: str
    difficulty: Difficulty
    # Exercism's own 1–10 scale.
    level: int
    xp: int
    topics: list[str]
    solved: bool


class ExerciseList(CamelModel):
    language: LibraryLanguage
    exercises: list[ExerciseSummary]
    source_url: str
    license: str = "MIT"


class ExerciseDetail(CamelModel):
    language: LibraryLanguage
    slug: str
    name: str
    blurb: str
    difficulty: Difficulty
    level: int
    xp: int
    topics: list[str]
    # Markdown, straight from Exercism.
    instructions: str
    # The files the learner edits (name -> starter content).
    solution: dict[str, str]
    # The test suite their code is graded against (shown read-only).
    tests: dict[str, str]
    solved: bool
    exercism_url: str
    source: str | None = None
    source_url: str | None = None


class ExerciseSubmission(CamelModel):
    # name -> content; only names that belong to the exercise's solution files are used.
    files: dict[str, str] = Field(min_length=1)


class ExerciseTestResult(CamelModel):
    name: str
    status: TestStatus
    message: str | None = None


class ExerciseRunResult(CamelModel):
    status: Literal["passed", "failed", "error"]
    tests: list[ExerciseTestResult]
    passed_count: int
    total: int
    stdout: str = ""
    error: str | None = None
    runtime_ms: int | None = None
    # Submit only.
    awarded_xp: int | None = None
    balance: XpBalance | None = None
