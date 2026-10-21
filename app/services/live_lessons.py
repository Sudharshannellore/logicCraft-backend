"""Live teaching text for curated lessons.

The world map, XP, quizzes and Try-it checks stay as written in the catalog. What comes from the
outside is the lesson's explanation: the matching concept doc from the language's Exercism track
(MIT-licensed, read from GitHub and cached), or, when the track has no such concept, the MDN
reference (JavaScript / TypeScript). Any failure leaves the curated text untouched.
"""

import logging

from app.domain.languages import language as language_info
from app.domain.live_lessons import best_concept, plain_intro, trim_markdown
from app.integrations.exercism.client import ExercismClient, ExercismUnavailable
from app.schemas.learning import Lesson
from app.services.tutorials import TutorialService

logger = logging.getLogger(__name__)


class LiveLessonService:
    def __init__(self, exercism: ExercismClient, tutorials: TutorialService):
        self.exercism = exercism
        self.tutorials = tutorials

    async def enrich(self, lesson: Lesson, language_id: str | None) -> Lesson:
        try:
            return await self._enrich(lesson, language_id) or lesson
        except Exception as exc:  # a lesson must always load, whatever the outside world is doing
            logger.warning("Live content failed for lesson %s: %r", lesson.id, exc)
            return lesson

    async def _enrich(self, lesson: Lesson, language_id: str | None) -> Lesson | None:
        info = language_info(language_id)
        if info is None:
            return None
        try:
            concepts = await self.exercism.concepts(info.exercism_track)
            slug = best_concept(lesson.title, [(c.slug, c.name) for c in concepts])
            doc = await self.exercism.concept_doc(info.exercism_track, slug) if slug else None
        except ExercismUnavailable:
            doc = None
        if doc:
            markdown = trim_markdown(doc.markdown)
            return lesson.model_copy(
                update={
                    "explanation": plain_intro(markdown) or lesson.explanation,
                    "live_content": markdown,
                    "live_source_name": f"Exercism · {info.name}",
                    "live_source_url": doc.url,
                    "source": "live",
                }
            )
        reference = await self.tutorials.reference(lesson.title, language_id)
        # Wikipedia is too general to replace a hand-written lesson; MDN is language-specific.
        if not reference or reference.provider != "mdn":
            return None
        return lesson.model_copy(
            update={
                "explanation": plain_intro(reference.summary) or lesson.explanation,
                "live_content": reference.summary.strip(),
                "live_source_name": "MDN Web Docs",
                "live_source_url": reference.url,
                "source": "live",
            }
        )
