from typing import Literal

from app.schemas.common import CamelModel, Difficulty, NodeState, XpBalance
from app.schemas.tutorials import TutorialImage, TutorialReference, TutorialResource

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
    # "language" = Exercism-based course in a language; "framework" = built from a framework's open-source docs.
    kind: Literal["language", "framework"] = "language"


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


class LessonExercise(CamelModel):
    """The graded exercise a live lesson ends with; solve it through the practice library endpoints."""

    language: str
    slug: str
    name: str
    url: str
    gradable: bool


class Lesson(CamelModel):
    id: str
    course_id: str
    module_id: str
    title: str
    concept: str
    explanation: str
    code_example: str = ""
    xp: int | None = None
    estimated_minutes: int | None = None
    # Teaching text pulled live from an open-source syllabus (Markdown), with where it came from.
    live_content: str | None = None
    live_source_name: str | None = None
    live_source_url: str | None = None
    exercise: LessonExercise | None = None
    completed: bool = False


class LessonResources(CamelModel):
    lesson_id: str
    reference: TutorialReference | None
    resources: list[TutorialResource]
    images: list[TutorialImage] = []


class LessonCompletion(CamelModel):
    lesson_id: str
    awarded: int
    balance: XpBalance
    course_progress_percent: int
