"""Courses, world maps and lessons.

Curated lessons live in the catalog. A world-map topic without a curated lesson gets one
assembled from external references (MDN / Wikipedia), so new topics are playable immediately.
Every lesson can also pull live tutorials from the external platforms.
"""

import hashlib
import re

from app.core.errors import ConflictError, NotFoundError, UnprocessableError
from app.repositories.catalog import CoursePathRepository, CourseRepository, LessonRepository
from app.repositories.progress import CourseProgressRepository
from app.repositories.users import UserRepository
from app.schemas.learning import (
    Course,
    CoursePath,
    Lesson,
    LessonCompletion,
    LessonResources,
    PathNode,
    PathZone,
    Quiz,
    QuizAnswerResult,
    TryItResult,
)
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


def _first_sentence(text: str) -> str:
    return re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0]


class LearningService:
    def __init__(
        self,
        courses: CourseRepository,
        paths: CoursePathRepository,
        lessons: LessonRepository,
        progress: CourseProgressRepository,
        users: UserRepository,
        wallet: WalletService,
        tracker: ProgressTracker,
        tutorials: TutorialService,
    ):
        self.courses = courses
        self.paths = paths
        self.lessons = lessons
        self.progress = progress
        self.users = users
        self.wallet = wallet
        self.tracker = tracker
        self.tutorials = tutorials

    # --- Courses & map -----------------------------------------------------------------

    async def _zones(self, user_id: str, course_id: str) -> list[PathZone]:
        path = await self.paths.for_course(course_id)
        if not path:
            return []
        state = await self.progress.get(user_id, course_id)
        return apply_progress(path.zones, set(state["completed_nodes"]), set(state["defeated_bosses"]))

    async def list_courses(self, user_id: str) -> list[Course]:
        return [
            c.model_copy(update={"progress_percent": progress_percent(await self._zones(user_id, c.id))})
            for c in await self.courses.list()
        ]

    async def get_course(self, user_id: str, course_id: str) -> Course:
        course = await self.courses.get(course_id)
        if not course:
            raise NotFoundError("Course not found.")
        return course.model_copy(update={"progress_percent": progress_percent(await self._zones(user_id, course_id))})

    async def course_path(self, user_id: str, course_id: str) -> list[PathZone]:
        if not await self.courses.get(course_id):
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

    # --- Lessons -------------------------------------------------------------------------

    async def _locate(self, lesson_id: str) -> tuple[CoursePath, PathZone, PathNode] | None:
        path = await self.paths.find_one({"zones.nodes.id": lesson_id})
        if not path:
            return None
        for zone in path.zones:
            for node in zone.nodes:
                if node.id == lesson_id:
                    return path, zone, node
        return None

    async def _lesson(self, lesson_id: str) -> tuple[Lesson, PathNode | None, str | None]:
        located = await self._locate(lesson_id)
        node = located[2] if located else None
        course_id = located[0].course_id if located else None
        lesson = await self.lessons.get(lesson_id)
        if lesson is None:
            if not located:
                raise NotFoundError("Lesson not found.")
            lesson = await self._generate(located[0], node)
        if node:
            lesson = lesson.model_copy(
                update={
                    "xp": lesson.xp or node.xp_reward,
                    "estimated_minutes": lesson.estimated_minutes or node.estimated_minutes,
                }
            )
        return lesson, node, course_id or lesson.course_id

    async def _generate(self, path: CoursePath, node: PathNode) -> Lesson:
        """A lesson for a topic nobody has written up yet, built from MDN/Wikipedia."""
        course = await self.courses.get(path.course_id)
        language = course.language if course else None
        reference = await self.tutorials.reference(node.title, language)
        if not reference:
            raise NotFoundError(f'No lesson for "{node.title}" yet, and no external reference was reachable.')
        summary = reference.summary.strip()
        correct = _first_sentence(summary)
        others = [
            _first_sentence(other.explanation) for other in await self.lessons.list({"course_id": path.course_id})
        ]
        distractors = [o for o in others if o and o != correct][:3]
        if len(distractors) < 3:
            raise NotFoundError(f'No lesson for "{node.title}" yet.')
        correct_index = int(hashlib.sha1(node.id.encode()).hexdigest(), 16) % 4
        options = distractors[:correct_index] + [correct] + distractors[correct_index:]
        return Lesson(
            id=node.id,
            course_id=path.course_id,
            module_id="",
            title=node.title,
            concept=node.title,
            explanation=summary,
            code_example=f"# Worked examples for {node.title} are in the tutorials linked below.",
            quiz=Quiz(
                question=f"Which statement describes {node.title}?",
                options=options,
                correct_index=correct_index,
                explanation=f"From {reference.provider.title()}: {correct}",
            ),
            key_points=[s for s in re.split(r"(?<=[.!?])\s", summary) if s][:3],
            source="generated",
        )

    async def lesson_content(self, lesson_id: str) -> Lesson:
        """The lesson itself, without any player state (curated or generated)."""
        return (await self._lesson(lesson_id))[0]

    async def get_lesson(self, user_id: str, lesson_id: str) -> Lesson:
        lesson, _, course_id = await self._lesson(lesson_id)
        state = await self.progress.get(user_id, course_id) if course_id else {"completed_nodes": []}
        completed = lesson_id in state["completed_nodes"] or await self.wallet.has_reward(
            user_id, f"lesson:{lesson_id}"
        )
        return lesson.model_copy(update={"completed": completed})

    async def lesson_resources(self, lesson_id: str, limit: int) -> LessonResources:
        lesson, _, course_id = await self._lesson(lesson_id)
        course = await self.courses.get(course_id) if course_id else None
        language = course.language if course else None
        search = await self.tutorials.search(lesson.concept, language=language, limit=limit)
        reference = await self.tutorials.reference(lesson.concept, language)
        return LessonResources(lesson_id=lesson_id, reference=reference, resources=search.resources)

    async def check_try_it(self, lesson_id: str, code: str) -> TryItResult:
        lesson, _, _ = await self._lesson(lesson_id)
        if not lesson.try_it:
            raise UnprocessableError("This lesson has no Try it exercise.")
        hints = [c.hint for c in lesson.try_it.checks if not re.search(c.pattern, code)]
        return TryItResult(passed=not hints, hints=hints, expected_output=lesson.try_it.expected_output)

    async def answer_quiz(self, lesson_id: str, answer_index: int) -> QuizAnswerResult:
        lesson, _, _ = await self._lesson(lesson_id)
        if answer_index >= len(lesson.quiz.options):
            raise UnprocessableError("That answer doesn't exist.")
        return QuizAnswerResult(
            correct=answer_index == lesson.quiz.correct_index,
            correct_index=lesson.quiz.correct_index,
            explanation=lesson.quiz.explanation,
        )

    async def complete_lesson(self, user_id: str, lesson_id: str) -> LessonCompletion:
        lesson, node, course_id = await self._lesson(lesson_id)
        if node and course_id:
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
        percent = progress_percent(await self._zones(user_id, course_id)) if course_id else 0
        return LessonCompletion(
            lesson_id=lesson.id, awarded=award.awarded, balance=award.balance, course_progress_percent=percent
        )
