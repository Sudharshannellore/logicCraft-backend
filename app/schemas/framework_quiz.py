"""Framework practice and challenges: quizzes made from a framework's own docs (see domain/framework_quiz.py)."""

from typing import Literal

from pydantic import Field

from app.schemas.common import CamelModel, EpochMs, XpBalance

QuizKind = Literal["practice", "daily", "zone"]
QuizStatus = Literal["not_started", "in_progress", "passed", "failed", "timed_out"]


class QuizQuestionOut(CamelModel):
    """A question as the learner sees it: no answer."""

    id: str
    prompt: str
    options: list[str]
    lesson_id: str


class FrameworkQuiz(CamelModel):
    id: str
    kind: QuizKind
    title: str
    description: str
    course_id: str
    course_title: str
    language: str
    # Practice quizzes: the lesson they cover. Zone bosses: the boss.
    lesson_id: str | None = None
    boss_id: str | None = None
    boss_name: str | None = None
    boss_sprite: str | None = None
    question_count: int
    pass_percent: int
    # None = untimed.
    time_limit_minutes: int | None = None
    # XP for the first pass (a zone boss pays its map reward).
    xp: int
    # False when the lesson has too little to quiz on: read it instead.
    available: bool = True
    # A zone boss whose zone still has uncleared topics.
    locked: bool = False
    # A zone boss already beaten.
    defeated: bool = False
    # Whether a failed or timed-out run can be started again.
    retry: bool = False
    status: QuizStatus = "not_started"
    best_percent: int | None = None
    tries: int = 0
    deadline: EpochMs | None = None
    # Included when there is something to answer now: always for practice, only mid-run for timed quizzes.
    questions: list[QuizQuestionOut] | None = None
    # When a daily quiz rotates out.
    ends_at: EpochMs | None = None


class QuizAnswer(CamelModel):
    question_id: str = Field(min_length=1, max_length=40)
    option_index: int = Field(ge=0, le=9)


class QuizSubmission(CamelModel):
    answers: list[QuizAnswer] = Field(max_length=40)


class QuestionResult(CamelModel):
    question_id: str
    correct: bool
    chosen: int | None
    correct_index: int
    # The doc's own sentence, with the answer in it.
    explanation: str
    lesson_id: str


class QuizResult(CamelModel):
    quiz: FrameworkQuiz
    correct: int
    total: int
    percent: int
    passed: bool
    results: list[QuestionResult]
    awarded_xp: int = 0
    balance: XpBalance


class FrameworkSummary(CamelModel):
    """A framework course in the Practice and Challenges pickers."""

    course_id: str
    title: str
    language: str
    topics: int
    solved: int
    progress_percent: int


class PracticeTopic(CamelModel):
    lesson_id: str
    title: str
    section: str
    solved: bool
    best_percent: int | None = None
