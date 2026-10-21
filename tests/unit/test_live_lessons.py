"""Live lesson text: topic → concept matching, Markdown tidying, and the service's fallbacks."""

import pytest

from app.domain.live_lessons import best_concept, plain_intro, trim_markdown
from app.integrations.exercism.client import ConceptDoc, ConceptSummary, ExercismUnavailable
from app.schemas.learning import Lesson, Quiz
from app.schemas.tutorials import TutorialReference
from app.services.live_lessons import LiveLessonService

CONCEPTS = [
    ("basics", "Basics"),
    ("conditionals", "Conditionals"),
    ("for-loops", "For Loops"),
    ("lists", "Lists"),
    ("dicts", "Dicts"),
    ("type-casting", "Type Casting"),
]


@pytest.mark.parametrize(
    ("title", "slug"),
    [
        ("For Loops", "for-loops"),
        ("Lists", "lists"),
        ("List", "lists"),
        ("Loops", "for-loops"),
        ("Basics", "basics"),
        ("DOM Basics", None),
        ("Variables & Types", None),
        ("Goroutines", None),
    ],
)
def test_topics_match_only_a_concept_that_really_covers_them(title, slug):
    assert best_concept(title, CONCEPTS) == slug


def test_front_matter_is_dropped_and_long_text_is_cut_on_a_paragraph():
    assert trim_markdown("---\ntitle: x\n---\n# Hi\n\nBody").startswith("# Hi")
    long = "\n\n".join(f"paragraph {i} " + "x" * 500 for i in range(40))
    out = trim_markdown(long)
    assert len(out) < 8_100 and out.endswith("…")


def test_plain_intro_skips_headings_and_code_and_strips_markup():
    md = "# About\n\nA **list** is [ordered](http://x).\n\n```py\nx = 1\n```\n\n- bullet\n\nSecond paragraph."
    assert plain_intro(md) == "A list is ordered. Second paragraph."


def test_plain_intro_is_capped_at_a_sentence():
    out = plain_intro(("This is a sentence. " * 100).strip())
    assert len(out) <= 600 and out.endswith(".")


class FakeExercism:
    def __init__(self, concepts=(), docs=None, down=False):
        self._concepts = [ConceptSummary(*c) for c in concepts]
        self._docs = docs or {}
        self._down = down

    async def concepts(self, track):
        if self._down:
            raise ExercismUnavailable("offline")
        return self._concepts

    async def concept_doc(self, track, slug):
        return ConceptDoc(slug, self._docs[slug], f"https://exercism.org/tracks/{track}/concepts/{slug}")


class FakeTutorials:
    def __init__(self, provider="mdn"):
        self.provider = provider

    async def reference(self, query, language=None):
        return TutorialReference(provider=self.provider, title=query, summary="Reference text.", url="https://ref")


def lesson(title="For Loops"):
    return Lesson(
        id="py3",
        course_id="python-basics",
        module_id="m1",
        title=title,
        concept=title,
        explanation="Hand-written.",
        code_example="",
        quiz=Quiz(question="?", options=["a", "b"], correct_index=0),
    )


async def test_matching_concept_replaces_the_text_and_keeps_the_rest():
    exercism = FakeExercism([("for-loops", "For Loops")], {"for-loops": "# Loops\n\nLoop over things."})
    out = await LiveLessonService(exercism, FakeTutorials()).enrich(lesson(), "python")
    assert out.source == "live" and out.explanation == "Loop over things."
    assert out.live_content.startswith("# Loops")
    assert out.live_source_url == "https://exercism.org/tracks/python/concepts/for-loops"
    assert out.quiz == lesson().quiz


async def test_unmatched_topic_falls_back_to_mdn_but_not_to_wikipedia():
    mdn = LiveLessonService(FakeExercism([("lists", "Lists")]), FakeTutorials("mdn"))
    assert (await mdn.enrich(lesson(), "javascript")).live_source_name == "MDN Web Docs"
    wiki = LiveLessonService(FakeExercism([("lists", "Lists")]), FakeTutorials("wikipedia"))
    assert (await wiki.enrich(lesson(), "python")).source == "curated"


async def test_outage_or_unknown_language_leaves_the_curated_lesson():
    down = LiveLessonService(FakeExercism(down=True), FakeTutorials("wikipedia"))
    assert (await down.enrich(lesson(), "python")).explanation == "Hand-written."
    assert (await down.enrich(lesson(), "cobol")).source == "curated"
