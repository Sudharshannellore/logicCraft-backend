"""Live courses: the syllabus → map rules, and the service that serves a course and its lessons."""

import pytest

from app.core.errors import NotFoundError, ServiceUnavailableError
from app.domain.languages import LANGUAGES
from app.domain.live_courses import (
    MAX_CONCEPT_TOPICS,
    TARGET_TOPICS,
    build_live_course,
    parse_id,
    select_topics,
)
from app.domain.live_lessons import absolutize_images, plain_intro, trim_markdown
from app.integrations.exercism.client import (
    ConceptDoc,
    ExerciseFiles,
    ExerciseSummary,
    ExercismUnavailable,
    Syllabus,
    SyllabusConceptExercise,
)
from app.integrations.tutorials.wikipedia import WikipediaProvider
from app.services import live_courses
from app.services.live_courses import LiveCourseService

PYTHON = LANGUAGES["python"]


def concept(slug, concepts=(), prerequisites=()):
    return SyllabusConceptExercise(slug, slug.title(), list(concepts), list(prerequisites))


def practice(slug, level):
    return ExerciseSummary(slug, slug.title(), level, [])


def big_practice(n=60):
    return [practice(f"p{i:02d}", 1 + i * 10 // n) for i in range(n)]


def test_ids_round_trip():
    assert parse_id("live-python") == ("python", "")
    assert parse_id("live-python-two-fer") == ("python", "two-fer")
    assert parse_id("python-basics") is None
    assert parse_id("live-") is None


def test_concept_exercises_come_after_the_ones_that_teach_their_prerequisites():
    syllabus = Syllabus(
        concept_exercises=[
            concept("loops", ["loops"], ["basics"]),
            concept("lists", ["lists"], ["loops", "basics"]),
            concept("basics", ["basics"]),
        ],
        practice=big_practice(),
    )
    order = [t[0] for t in select_topics(syllabus) if t[2] == "concept"]
    assert order == ["basics", "loops", "lists"]


def test_a_prerequisite_cycle_or_an_unknown_prerequisite_cannot_hang_or_drop_exercises():
    syllabus = Syllabus(
        [concept("a", ["a"], ["b"]), concept("b", ["b"], ["a"]), concept("c", ["c"], ["never-taught"])],
        big_practice(),
    )
    assert {t[0] for t in select_topics(syllabus) if t[2] == "concept"} == {"a", "b", "c"}


def test_course_size_is_bounded_and_practice_spans_easy_to_hard():
    syllabus = Syllabus([concept(f"c{i}", [f"k{i}"]) for i in range(40)], big_practice())
    topics = select_topics(syllabus)
    kinds = [t[2] for t in topics]
    assert kinds.count("concept") == MAX_CONCEPT_TOPICS and len(topics) == TARGET_TOPICS
    levels = [t[3] for t in topics if t[2] == "practice"]
    assert levels == sorted(levels) and levels[0] <= 2 and levels[-1] >= 8


def test_a_track_without_a_syllabus_is_taught_through_practice_exercises():
    live = build_live_course(PYTHON, Syllabus([], big_practice()))
    assert live and len(live.topics) == TARGET_TOPICS
    assert all(t.kind == "practice" for t in live.topics.values())


def test_tiny_tracks_make_no_course():
    assert build_live_course(PYTHON, Syllabus([], [practice("a", 1), practice("b", 2)])) is None


def test_map_is_well_formed_and_never_gets_easier():
    live = build_live_course(PYTHON, Syllabus([concept(f"c{i}", [f"k{i}"]) for i in range(10)], big_practice()))
    course, zones = live.course, live.path.zones
    assert course.id == "live-python" and course.language == "python"
    ranks = {"easy": 0, "medium": 1, "hard": 2}
    assert [ranks[z.difficulty] for z in zones] == sorted(ranks[z.difficulty] for z in zones)
    nodes = [n for z in zones for n in z.nodes]
    assert all(len(z.nodes) >= 2 for z in zones)
    assert len({n.id for n in nodes}) == len(nodes) == len(live.topics)
    assert all(n.lesson_id == n.id and n.id.startswith("live-python-") for n in nodes)
    assert len({z.boss.id for z in zones}) == len(zones)
    assert course.total_xp == sum(n.xp_reward for n in nodes) + sum(z.boss.xp_reward for z in zones)
    assert {m.id for m in course.modules} == {t.module_id for t in live.topics.values()}


def test_front_matter_is_dropped_and_long_text_is_cut_on_a_paragraph():
    assert trim_markdown("---\ntitle: x\n---\n# Hi\n\nBody").startswith("# Hi")
    long = "\n\n".join(f"paragraph {i} " + "x" * 500 for i in range(40))
    out = trim_markdown(long)
    assert len(out) < 8_100 and out.endswith("…")


def test_plain_intro_skips_headings_and_code_and_is_capped_at_a_sentence():
    md = "# About\n\nA **list** is [ordered](http://x).\n\n```py\nx = 1\n```\n\n- bullet\n\nSecond paragraph."
    assert plain_intro(md) == "A list is ordered. Second paragraph."
    out = plain_intro(("This is a sentence. " * 100).strip())
    assert len(out) <= 600 and out.endswith(".")


def test_plain_intro_unwraps_reference_style_links():
    assert plain_intro("A [dynamic][typing] language.\n\n[typing]: https://x") == "A dynamic language."


# --- the service ----------------------------------------------------------------------------------------


class FakeExercism:
    def __init__(self, syllabus, down=False):
        self.syllabus_value, self.down, self.syllabus_calls = syllabus, down, 0

    async def syllabus(self, track):
        self.syllabus_calls += 1
        if self.down:
            raise ExercismUnavailable("offline")
        return self.syllabus_value

    async def exercise(self, track, slug):
        if slug == "gone":
            return None
        return ExerciseFiles(
            slug,
            slug.title(),
            "A blurb.",
            "Do the task.",
            {"a.py": ""},
            {"t.py": ""},
            {},
            None,
            None,
            introduction="Intro text.",
        )

    async def concept_doc(self, track, slug):
        if slug == "documented":
            return ConceptDoc(slug, "# Doc\n\nTeaches it.\n\n```python\nx = 1\n```", f"https://x/{slug}")
        return None


@pytest.fixture(autouse=True)
def _fresh_memo():
    live_courses.clear_memo()
    yield
    live_courses.clear_memo()


def service(**kwargs):
    syllabus = Syllabus(
        [concept("documented", ["documented"]), concept("plain", ["plain"]), concept("gone", ["gone"])], big_practice()
    )
    return LiveCourseService(FakeExercism(syllabus, **kwargs), lambda language_id: language_id == "python")


async def test_any_language_with_a_track_gets_a_course_and_other_ids_get_none():
    svc = service()
    assert (await svc.for_id("live-go-whatever")).course.language == "go"
    assert await svc.for_id("python-basics") is None
    assert await svc.course("cobol") is None
    assert len(await svc.courses()) == len(LANGUAGES)


async def test_built_course_is_remembered_between_requests():
    svc = service()
    await svc.course("python")
    await svc.course("python")
    assert svc.exercism.syllabus_calls == 1


async def test_outage_fails_a_direct_request_but_only_thins_the_list():
    svc = service(down=True)
    with pytest.raises(ServiceUnavailableError):
        await svc.course("python")
    assert await svc.courses() == []


async def test_concept_lesson_teaches_from_the_concept_doc_and_ends_with_a_graded_exercise():
    svc = service()
    live = await svc.course("python")
    lesson = await svc.lesson(live, "live-python-documented")
    assert lesson.explanation == "Teaches it." and lesson.code_example == "x = 1"
    assert lesson.live_source_url == "https://x/documented" and lesson.live_content.startswith("# Doc")
    assert lesson.exercise.slug == "documented" and lesson.exercise.gradable
    assert lesson.course_id == "live-python" and lesson.module_id == "live-python-m1"


async def test_lesson_without_a_concept_doc_falls_back_to_the_exercise_introduction():
    svc = service()
    lesson = await svc.lesson(await svc.course("python"), "live-python-plain")
    assert lesson.explanation == "Intro text." and lesson.live_source_url.endswith("/exercises/plain")


async def test_missing_exercise_or_topic_is_not_found_and_other_languages_are_not_gradable_here():
    svc = service()
    live = await svc.course("python")
    with pytest.raises(NotFoundError):
        await svc.lesson(live, "live-python-gone")
    with pytest.raises(NotFoundError):
        await svc.lesson(live, "live-python-nope")
    go = await svc.lesson(await svc.course("go"), "live-go-plain")
    assert go.exercise.gradable is False


# --- pictures -------------------------------------------------------------------------------------------


def test_relative_image_links_point_at_the_source_repository_and_others_are_untouched():
    base = "https://raw.githubusercontent.com/exercism/python/main/concepts/lists/"
    text = '![a](img/a.png) ![b](https://x/b.png "t") ![c](//cdn/c.png) ![d](../shared/d.svg) [link](page.md)'
    assert absolutize_images(text, base) == (
        f"![a]({base}img/a.png) ![b](https://x/b.png \"t\") ![c](//cdn/c.png) "
        "![d](https://raw.githubusercontent.com/exercism/python/main/concepts/shared/d.svg) [link](page.md)"
    )


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status_code = payload, status

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class FakeWikipedia:
    """Search finds one page; its media list has a diagram, site furniture and a non-image."""

    async def get(self, url, params=None):
        if url.endswith("/search/page"):
            return FakeResponse({"pages": [{"key": "Linked_list", "title": "Linked list", "description": "data structure"}]})
        item = lambda title, **extra: {"type": "image", "showInGallery": True, "title": title, **extra}  # noqa: E731
        sources = [{"src": "//upload.wikimedia.org/a-320.png"}, {"src": "//upload.wikimedia.org/a-640.png"}]
        return FakeResponse(
            {
                "items": [
                    item("File:Node-diagram.svg", srcset=sources, caption={"text": " A node "}),
                    item("File:Commons-logo.svg", srcset=sources),
                    {"type": "video", "title": "File:Clip.webm", "srcset": sources},
                ]
            }
        )


async def test_wikipedia_images_keep_diagrams_largest_size_with_a_credit_link():
    images = await WikipediaProvider(FakeWikipedia()).images("Linked lists", "python", 4)
    assert [(i.url, i.caption, i.source_url) for i in images] == [
        (
            "https://upload.wikimedia.org/a-640.png",
            "A node",
            "https://en.wikipedia.org/wiki/File:Node-diagram.svg",
        )
    ]


async def test_a_concept_name_with_no_content_words_gets_no_pictures():
    assert await WikipediaProvider(FakeWikipedia()).images("Basics", "python", 4) == []
