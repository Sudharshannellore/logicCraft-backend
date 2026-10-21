from app.domain.career_paths import StepState
from app.schemas.common import CamelModel
from app.schemas.learning import Course


class PathStep(CamelModel):
    course: Course
    state: StepState


class CareerPathSummary(CamelModel):
    id: str
    title: str
    tagline: str
    description: str
    sprite: str
    total_steps: int
    completed_steps: int
    progress_percent: int
    # The learner chose this path (they can leave it any time).
    enrolled: bool
    # Suggested because of what the learner has already done in it, and why.
    recommended: bool
    reason: str | None = None
    course_titles: list[str]


class CareerPathDetail(CareerPathSummary):
    steps: list[PathStep]
