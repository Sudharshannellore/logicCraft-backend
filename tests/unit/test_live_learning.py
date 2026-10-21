"""LearningService serves live courses beside the seeded ones, with the same progress and XP rules."""

import pytest

from app.core.errors import ConflictError, NotFoundError
from app.integrations.exercism.client import ExerciseFiles, ExerciseSummary, Syllabus, SyllabusConceptExercise
from app.schemas.common import XpAward, XpBalance
from app.services import live_courses
from app.services.learning import LearningService
from app.services.live_courses import LiveCourseService


class Progress:
    def __init__(self):
        self.state = {"completed_nodes": [], "defeated_bosses": []}

    async def get(self, user_id, course_id):
        return self.state

    async def for_user(self, user_id):
        return {"live-python": self.state} if self.state["completed_nodes"] else {}

    async def add(self, user_id, course_id, *, node_id=None, boss_id=None):
        if node_id:
            self.state["completed_nodes"].append(node_id)


class Wallet:
    def __init__(self):
        self.earned = []

    async def has_reward(self, *_):
        return False

    async def earn(self, user_id, amount, reason, **kwargs):
        self.earned.append((amount, kwargs["reward_key"]))
        return XpAward(awarded=amount, balance=XpBalance(xp=amount, lifetime_xp=amount))


class Tracker:
    async def record(self, *_):
        pass


class FakeExercism:
    async def syllabus(self, track):
        return Syllabus(
            [SyllabusConceptExercise(f"c{i}", f"C{i}", [f"k{i}"], [f"k{i - 1}"] if i else []) for i in range(8)],
            [ExerciseSummary(f"p{i}", f"P{i}", 1 + i, []) for i in range(30)],
        )

    async def exercise(self, track, slug):
        return ExerciseFiles(slug, slug.upper(), "Blurb.", "Task.", {"a.py": ""}, {"t.py": ""}, {}, None, None)

    async def concept_doc(self, track, slug):
        return None


@pytest.fixture
def learning():
    live_courses.clear_memo()
    wallet = Wallet()
    service = LearningService(
        Progress(),
        None,
        wallet,
        Tracker(),
        None,
        LiveCourseService(FakeExercism(), lambda language_id: True),
    )
    service.wallet_spy = wallet
    yield service
    live_courses.clear_memo()


async def test_live_courses_are_listed_and_have_a_map_with_only_the_first_topic_open(learning):
    courses = await learning.list_courses("u1")
    assert len(courses) == 13 and {c.id for c in courses} >= {"live-python", "live-sql"}
    zones = await learning.course_path("u1", "live-python")
    assert zones[0].nodes[0].state == "current" and zones[0].nodes[1].state == "locked"
    assert zones[1].nodes[0].state == "locked" and zones[0].boss.state == "locked"


async def test_a_live_lesson_loads_with_the_node_xp_and_its_exercise(learning):
    zones = await learning.course_path("u1", "live-python")
    node = zones[0].nodes[0]
    lesson = await learning.get_lesson("u1", node.id)
    assert lesson.xp == node.xp_reward and lesson.exercise.slug == "c0"


async def test_completing_a_live_lesson_pays_once_and_opens_the_next_topic(learning):
    zones = await learning.course_path("u1", "live-python")
    first, second = zones[0].nodes[0], zones[0].nodes[1]
    with pytest.raises(ConflictError):
        await learning.complete_lesson("u1", second.id)  # still locked
    done = await learning.complete_lesson("u1", first.id)
    assert done.awarded == first.xp_reward and done.course_progress_percent > 0
    assert learning.wallet_spy.earned == [(first.xp_reward, f"lesson:{first.id}")]
    assert (await learning.course_path("u1", "live-python"))[0].nodes[1].state == "current"


async def test_unknown_live_ids_are_not_found(learning):
    for call in (
        learning.get_course("u1", "live-cobol"),
        learning.get_lesson("u1", "live-python-nope"),
        learning.get_lesson("u1", "plain-id"),
    ):
        with pytest.raises(NotFoundError):
            await call
