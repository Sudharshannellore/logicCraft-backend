"""Courses, world maps and lessons.

All of them are live: each language's course is built on demand from its open-source Exercism syllabus
(see live_courses.py), so there is no course catalog to maintain. This service adds the player's side:
which topics are open, lesson completion and XP, zone bosses, and extra tutorials from external platforms.
"""

import asyncio

from app.core.errors import ConflictError, NotFoundError
from app.repositories.progress import CourseProgressRepository
from app.repositories.users import UserRepository
from app.schemas.learning import (
    Course,
    Lesson,
    LessonCompletion,
    LessonResources,
    PathNode,
    PathZone,
)
from app.services.live_courses import LiveCourseService
from app.services.quests import ProgressTracker
from app.services.tutorials import TutorialService
from app.services.wallet import WalletService

DEFAULT_LESSON_XP = 50


def apply_progress(zones: list[PathZone], completed: set[str], defeated: set[str]) -> list[PathZone]:
    """Fills node/boss states: clear topics in order, beat the zone's boss to open the next zone."""
    result: list[PathZone] = []
    zone_open = True
    for zone in zones:
        current_given = False
        nodes = []
        for node in zone.nodes:
            if node.id in completed:
                state = "completed"
            elif zone_open and not current_given:
                state, current_given = "current", True
            else:
                state = "locked"
            nodes.append(node.model_copy(update={"state": state}))
        all_cleared = all(n.state == "completed" for n in nodes)
        if zone.boss.id in defeated:
            boss_state = "completed"
        elif zone_open and all_cleared:
            boss_state = "current"
        else:
            boss_state = "locked"
        result.append(
            zone.model_copy(update={"nodes": nodes, "boss": zone.boss.model_copy(update={"state": boss_state})})
        )
        zone_open = zone_open and boss_state == "completed"
    return result


def progress_percent(zones: list[PathZone]) -> int:
    stops = [n.state for z in zones for n in z.nodes] + [z.boss.state for z in zones]
    return round(100 * stops.count("completed") / len(stops)) if stops else 0


class LearningService:
    def __init__(
        self,
        progress: CourseProgressRepository,
        users: UserRepository,
        wallet: WalletService,
        tracker: ProgressTracker,
        tutorials: TutorialService,
        live_courses: LiveCourseService,
    ):
        self.progress = progress
        self.users = users
        self.wallet = wallet
        self.tracker = tracker
        self.tutorials = tutorials
        self.live_courses = live_courses

    # --- Courses & map -----------------------------------------------------------------

    async def _course(self, course_id: str) -> Course | None:
        live = await self.live_courses.for_id(course_id)
        return live.course if live else None

    async def _zones(
        self, user_id: str, course_id: str, state: dict[str, list[str]] | None = None
    ) -> list[PathZone]:
        live = await self.live_courses.for_id(course_id)
        if not live:
            return []
        state = state or await self.progress.get(user_id, course_id)
        return apply_progress(live.path.zones, set(state["completed_nodes"]), set(state["defeated_bosses"]))

    async def list_courses(self, user_id: str) -> list[Course]:
        started = await self.progress.for_user(user_id)  # one query for every course, not one per course
        empty: dict[str, list[str]] = {"completed_nodes": [], "defeated_bosses": []}
        return [
            lc.course.model_copy(
                update={
                    "progress_percent": progress_percent(
                        apply_progress(
                            lc.path.zones,
                            set(started.get(lc.course.id, empty)["completed_nodes"]),
                            set(started.get(lc.course.id, empty)["defeated_bosses"]),
                        )
                    )
                }
            )
            for lc in await self.live_courses.courses()
        ]

    async def get_course(self, user_id: str, course_id: str) -> Course:
        course = await self._course(course_id)
        if not course:
            raise NotFoundError("Course not found.")
        return course.model_copy(update={"progress_percent": progress_percent(await self._zones(user_id, course_id))})

    async def course_path(self, user_id: str, course_id: str) -> list[PathZone]:
        if not await self._course(course_id):
            raise NotFoundError("Course not found.")
        return await self._zones(user_id, course_id)

    async def defeat_boss(
        self, user_id: str, course_id: str, boss_id: str, *, award_xp: bool = True
    ) -> LessonCompletion:
        """Opens the next zone. Called by the challenge service once the boss's rounds are beaten."""
        zones = await self.course_path(user_id, course_id)
        zone = next((z for z in zones if z.boss.id == boss_id), None)
        if not zone:
            raise NotFoundError("Boss not found on this map.")
        if zone.boss.state == "locked":
            raise ConflictError("Clear every topic in this zone before fighting its boss.")
        await self.progress.add(user_id, course_id, boss_id=boss_id)
        award = await self.wallet.earn(
            user_id,
            zone.boss.xp_reward if award_xp else 0,
            f"Defeated {zone.boss.name}",
            reward_key=f"boss:{boss_id}",
            activity=f"defeated {zone.boss.name}",
            sprite="trophy",
        )
        if award.awarded:
            await self.users.inc_stats(user_id, {"bosses_defeated": 1})
            await self.tracker.refresh_achievements(user_id)
        return LessonCompletion(
            lesson_id=boss_id,
            awarded=award.awarded,
            balance=award.balance,
            course_progress_percent=progress_percent(await self._zones(user_id, course_id)),
        )

    # --- Lessons -------------------------------------------------------------------------------

    async def _lesson(self, lesson_id: str) -> tuple[Lesson, PathNode, str]:
        live = await self.live_courses.for_id(lesson_id)
        node = next((n for z in live.path.zones for n in z.nodes if n.id == lesson_id), None) if live else None
        if not live or not node:
            raise NotFoundError("Lesson not found.")
        lesson = await self.live_courses.lesson(live, lesson_id)
        lesson = lesson.model_copy(update={"xp": node.xp_reward, "estimated_minutes": node.estimated_minutes})
        return lesson, node, live.course.id

    async def lesson_content(self, lesson_id: str) -> Lesson:
        """The lesson itself, without any player state."""
        return (await self._lesson(lesson_id))[0]

    async def get_lesson(self, user_id: str, lesson_id: str) -> Lesson:
        lesson, _, course_id = await self._lesson(lesson_id)
        state = await self.progress.get(user_id, course_id)
        completed = lesson_id in state["completed_nodes"] or await self.wallet.has_reward(
            user_id, f"lesson:{lesson_id}"
        )
        return lesson.model_copy(update={"completed": completed})

    async def lesson_resources(self, lesson_id: str, limit: int) -> LessonResources:
        lesson, _, course_id = await self._lesson(lesson_id)
        course = await self._course(course_id)
        language = course.language if course else None
        search, reference, images = await asyncio.gather(
            self.tutorials.search(lesson.concept, language=language, limit=limit),
            self.tutorials.reference(lesson.concept, language),
            self.tutorials.images(lesson.concept, language),
        )
        return LessonResources(lesson_id=lesson_id, reference=reference, resources=search.resources, images=images)

    async def complete_lesson(self, user_id: str, lesson_id: str) -> LessonCompletion:
        lesson, node, course_id = await self._lesson(lesson_id)
        zones = await self._zones(user_id, course_id)
        state = next((n.state for z in zones for n in z.nodes if n.id == node.id), "locked")
        if state == "locked":
            raise ConflictError("This topic is still locked — clear the earlier topics first.")
        await self.progress.add(user_id, course_id, node_id=node.id)
        award = await self.wallet.earn(
            user_id,
            lesson.xp or DEFAULT_LESSON_XP,
            f"Lesson: {lesson.title}",
            reward_key=f"lesson:{lesson.id}",
            activity=f"completed the lesson {lesson.title}",
            sprite="book",
        )
        if award.awarded:
            await self.tracker.record(user_id, "lesson_completed")
        return LessonCompletion(
            lesson_id=lesson.id,
            awarded=award.awarded,
            balance=award.balance,
            course_progress_percent=progress_percent(await self._zones(user_id, course_id)),
        )
