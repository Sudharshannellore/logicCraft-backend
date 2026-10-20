from pydantic import Field

from app.schemas.common import CamelModel, Difficulty, NodeState, XpBalance
from app.schemas.tutorials import TutorialReference, TutorialResource

# --- Courses & world map ---------------------------------------------------------


class CourseModule(CamelModel):
    id: str
    title: str
    lessons_count: int
    exercises_count: int
    completed_lessons: int = 0
    progress_percent: int = 0


class Course(CamelModel):
    id: str
    title: str
    world: str
    description: str
    # Language the course teaches — used to scope external tutorial searches.
    language: str
    progress_percent: int = 0
    total_xp: int
    modules: list[CourseModule]


class PathNode(CamelModel):
    id: str
    title: str
    state: NodeState = "locked"
    difficulty: Difficulty
    xp_reward: int
    estimated_minutes: int
    # The lesson the node opens (same as the node id).
    lesson_id: str


class PathBoss(CamelModel):
    id: str
    name: str
    sprite: str
    challenge: str
    stages: int
    xp_reward: int
    state: NodeState = "locked"


class PathZone(CamelModel):
    id: str
    name: str
    tagline: str
    difficulty: Difficulty
    nodes: list[PathNode]
    boss: PathBoss


class CoursePath(CamelModel):
    """Catalog document: a course's zones, in order. Node/boss states are filled per player."""

    course_id: str
    zones: list[PathZone]


# --- Lessons -------------------------------------------------------------------------


class Quiz(CamelModel):
    question: str
    options: list[str] = Field(min_length=2)
    correct_index: int
    explanation: str | None = None


class TryItCheck(CamelModel):
    pattern: str
    hint: str


class TryIt(CamelModel):
    prompt: str
    starter_code: str
    checks: list[TryItCheck]
    expected_output: str


class Lesson(CamelModel):
    id: str
    course_id: str
    module_id: str
    title: str
    concept: str
    explanation: str
    code_example: str
    quiz: Quiz
    xp: int | None = None
    estimated_minutes: int | None = None
    key_points: list[str] | None = None
    analogy: str | None = None
    code_walkthrough: list[str] | None = None
    try_it: TryIt | None = None
    # "curated" = written by the team; "generated" = assembled from external references.
    source: str = "curated"
    completed: bool = False


class LessonResources(CamelModel):
    lesson_id: str
    reference: TutorialReference | None
    resources: list[TutorialResource]


class TryItRequest(CamelModel):
    code: str = Field(max_length=20_000)


class TryItResult(CamelModel):
    passed: bool
    hints: list[str]
    expected_output: str


class QuizAnswerRequest(CamelModel):
    answer_index: int = Field(ge=0)


class QuizAnswerResult(CamelModel):
    correct: bool
    correct_index: int
    explanation: str | None


class LessonCompletion(CamelModel):
    lesson_id: str
    awarded: int
    balance: XpBalance
    course_progress_percent: int
