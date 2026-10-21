"""Courses that exist only in the open-source world: one per language, built from its Exercism track.

No catalog entry is needed. The course (zones, bosses, XP) is derived from the track's live `config.json`
(see app/domain/live_courses.py); a lesson's text is the concept doc and its practice is the concept
exercise, graded against Exercism's own tests. The built course is kept in memory for a few minutes on
top of the Mongo-cached syllabus, so a new language or a new Exercism exercise shows up on its own.
"""

import asyncio
import re
import time
from collections.abc import Callable

from app.core.errors import AppError, NotFoundError, ServiceUnavailableError
from app.domain.languages import LANGUAGES, LanguageInfo
from app.domain.live_courses import LiveCourse, Topic, build_live_course, parse_id
from app.domain.live_lessons import absolutize_images, plain_intro, trim_markdown
from app.integrations.exercism.client import ExercismClient, ExercismUnavailable, website_url
from app.schemas.learning import Lesson, LessonExercise
from app.services import docs_courses
from app.services.docs_courses import DocsCourseService

MEMO_SECONDS = 300
RAW_CONCEPTS = "https://raw.githubusercontent.com/exercism/{track}/main/concepts/{slug}/"
_CODE_BLOCK = re.compile(r"```[\w+#.-]*\n(.*?)```", re.S)

# language id -> (when built, course or None). Shared by every request in this process.
_memo: dict[str, tuple[float, LiveCourse | None]] = {}


def clear_memo() -> None:
    _memo.clear()
    docs_courses.clear_memo()


class LiveCourseService:
    def __init__(
        self, exercism: ExercismClient, gradable: Callable[[str], bool], docs: DocsCourseService | None = None
    ):
        self.exercism = exercism
        self.gradable = gradable
        self.docs = docs

    # --- Courses ----------------------------------------------------------------------------------------

    async def course(self, language_id: str) -> LiveCourse | None:
        """The language's live course; None when its track is too small to teach from."""
        info = LANGUAGES.get(language_id)
        if info is None:
            return None
        hit = _memo.get(language_id)
        if hit and time.monotonic() - hit[0] < MEMO_SECONDS:
            return hit[1]
        try:
            built = build_live_course(info, await self.exercism.syllabus(info.exercism_track))
        except ExercismUnavailable as exc:
            raise ServiceUnavailableError("Exercism can't be reached right now — try again in a minute.") from exc
        _memo[language_id] = (time.monotonic(), built)
        return built

    async def courses(self) -> list[LiveCourse]:
        """Every language's live course; one that can't be built right now is left out."""

        async def one(language_id: str) -> LiveCourse | None:
            try:
                return await self.course(language_id)
            except AppError:
                return None

        built = await asyncio.gather(*(one(language_id) for language_id in LANGUAGES))
        frameworks = await self.docs.courses() if self.docs else []
        return [*(c for c in built if c), *frameworks]

    async def for_id(self, item_id: str) -> LiveCourse | None:
        """The live course a course, zone or topic id belongs to; None for any other id (no I/O then)."""
        parsed = parse_id(item_id)
        if parsed:
            return await self.course(parsed[0])
        return await self.docs.for_id(item_id) if self.docs else None

    # --- Lessons ------------------------------------------------------------------------------------------

    async def _teaching_text(self, info: LanguageInfo, topic: Topic) -> tuple[str, str] | None:
        """(markdown, url) of the concept doc that teaches a concept exercise, if the track has one."""
        for concept in topic.concepts[:3]:
            doc = await self.exercism.concept_doc(info.exercism_track, concept)
            if doc:
                base = RAW_CONCEPTS.format(track=info.exercism_track, slug=concept)
                return absolutize_images(doc.markdown, base), doc.url
        return None

    async def lesson(self, live: LiveCourse, lesson_id: str) -> Lesson:
        if live.course.kind == "framework" and self.docs:
            return await self.docs.lesson(live, lesson_id)
        topic = live.topics.get(lesson_id)
        if topic is None:
            raise NotFoundError("Lesson not found.")
        info = LANGUAGES[live.course.language]
        try:
            files = await self.exercism.exercise(info.exercism_track, topic.slug)
            taught = await self._teaching_text(info, topic) if topic.kind == "concept" else None
        except ExercismUnavailable as exc:
            raise ServiceUnavailableError("Exercism can't be reached right now — try again in a minute.") from exc
        if files is None:
            raise NotFoundError(f'Exercism no longer has the "{topic.name}" exercise.')

        exercise_url = website_url(info.exercism_track, topic.slug)
        markdown, url = taught or (files.introduction or files.instructions or files.blurb, exercise_url)
        content = trim_markdown(markdown)
        code = _CODE_BLOCK.search(content)
        return Lesson(
            id=lesson_id,
            course_id=live.course.id,
            module_id=topic.module_id,
            title=topic.name,
            # What searches for tutorials and pictures: "For Loops", not an exercise's playful name.
            concept=topic.concepts[0].replace("-", " ").title() if topic.concepts else topic.name,
            explanation=plain_intro(content) or files.blurb or topic.name,
            code_example=code.group(1).strip() if code else "",
            source="live",
            live_content=content,
            live_source_name=f"Exercism · {info.name}",
            live_source_url=url,
            exercise=LessonExercise(
                language=info.id,
                slug=topic.slug,
                name=files.name,
                url=exercise_url,
                gradable=self.gradable(info.id),
            ),
        )
