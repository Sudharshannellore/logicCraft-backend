"""Career paths for a player: which courses make up each route, how far along they are, and which to suggest.

Progress isn't stored here. It is read from the courses themselves, so finishing a course in any order,
from any page, is reflected in every path that contains it. Only the player's choice of paths is saved.
"""

from app.core.clock import utcnow
from app.core.errors import NotFoundError
from app.domain.career_paths import (
    PATHS,
    PATHS_BY_ID,
    CareerPath,
    path_progress,
    reason_to_recommend,
    step_states,
)
from app.repositories.paths import PathEnrollmentRepository
from app.schemas.learning import Course
from app.schemas.paths import CareerPathDetail, CareerPathSummary, PathStep
from app.services.learning import LearningService

MIN_STEPS = 2  # a path with fewer available courses than this isn't worth showing


class PathService:
    def __init__(self, learning: LearningService, enrollments: PathEnrollmentRepository):
        self.learning = learning
        self.enrollments = enrollments

    def _courses_of(self, path: CareerPath, courses: dict[str, Course]) -> list[Course]:
        return [courses[cid] for cid in path.steps if cid in courses]

    def _summary(self, path: CareerPath, courses: dict[str, Course], enrolled: set[str]) -> CareerPathSummary | None:
        steps = self._courses_of(path, courses)
        if len(steps) < MIN_STEPS:
            return None
        percents = [c.progress_percent for c in steps]
        titles = [c.title for c in steps]
        done, percent = path_progress(percents)
        reason = reason_to_recommend(titles, percents)
        return CareerPathSummary(
            id=path.id,
            title=path.title,
            tagline=path.tagline,
            description=path.description,
            sprite=path.sprite,
            total_steps=len(steps),
            completed_steps=done,
            progress_percent=percent,
            enrolled=path.id in enrolled,
            recommended=reason is not None,
            reason=reason,
            course_titles=titles,
        )

    async def _state(self, user_id: str) -> tuple[dict[str, Course], set[str]]:
        courses = {c.id: c for c in await self.learning.list_courses(user_id)}
        return courses, await self.enrollments.ids(user_id)

    async def list(self, user_id: str) -> list[CareerPathSummary]:
        """Suggested paths first, then the ones the player chose, then the rest."""
        courses, enrolled = await self._state(user_id)
        summaries = [s for p in PATHS if (s := self._summary(p, courses, enrolled))]
        return sorted(summaries, key=lambda s: (not s.recommended, not s.enrolled))

    async def get(self, user_id: str, path_id: str) -> CareerPathDetail:
        path = PATHS_BY_ID.get(path_id)
        courses, enrolled = await self._state(user_id)
        summary = self._summary(path, courses, enrolled) if path else None
        if not path or not summary:
            raise NotFoundError("Path not found.")
        steps = self._courses_of(path, courses)
        states = step_states([c.progress_percent for c in steps])
        return CareerPathDetail(
            **summary.model_dump(),
            steps=[PathStep(course=c, state=s) for c, s in zip(steps, states, strict=True)],
        )

    async def enroll(self, user_id: str, path_id: str) -> CareerPathDetail:
        if path_id not in PATHS_BY_ID:
            raise NotFoundError("Path not found.")
        await self.enrollments.add(user_id, path_id, utcnow())
        return await self.get(user_id, path_id)

    async def leave(self, user_id: str, path_id: str) -> CareerPathDetail:
        if path_id not in PATHS_BY_ID:
            raise NotFoundError("Path not found.")
        await self.enrollments.remove(user_id, path_id)
        return await self.get(user_id, path_id)
