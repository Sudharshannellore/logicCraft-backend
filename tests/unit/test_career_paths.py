"""Career paths: the recipes, step states, recommendations, and the service over live courses."""

import pytest

from app.core.errors import NotFoundError
from app.domain.career_paths import PATHS, PATHS_BY_ID, path_progress, reason_to_recommend, step_states
from app.domain.docs_courses import SPECS
from app.domain.languages import LANGUAGES
from app.schemas.learning import Course
from app.services.paths import PathService


def test_every_path_step_is_a_real_language_or_framework_course():
    for path in PATHS:
        assert len(path.steps) >= 2 and len(set(path.steps)) == len(path.steps), path.id
        for step in path.steps:
            if step.startswith("live-"):
                assert step.removeprefix("live-") in LANGUAGES, (path.id, step)
            else:
                assert step.startswith("fw-") and step.removeprefix("fw-") in SPECS, (path.id, step)
    assert len(PATHS_BY_ID) == len(PATHS)


def test_each_framework_belongs_to_a_path():
    used = {s.removeprefix("fw-") for p in PATHS for s in p.steps if s.startswith("fw-")}
    assert used == set(SPECS)


def test_step_states_mark_finished_underway_next_and_the_rest():
    assert step_states([100, 40, 0, 0]) == ["completed", "in_progress", "available", "available"]
    assert step_states([100, 0, 0]) == ["completed", "next", "available"]
    assert step_states([0, 0]) == ["next", "available"]
    assert step_states([100, 100]) == ["completed", "completed"]
    # Taking a later course first doesn't lock anything.
    assert step_states([0, 0, 60]) == ["next", "available", "in_progress"]


def test_progress_counts_finished_courses_and_averages_the_rest():
    assert path_progress([100, 50, 0, 0]) == (1, 38)
    assert path_progress([100, 100]) == (2, 100)
    assert path_progress([]) == (0, 0)


def test_a_path_is_suggested_from_what_the_learner_already_did_in_it():
    assert reason_to_recommend(["Python", "SQL", "FastAPI"], [100, 0, 0]) == "You finished Python"
    assert reason_to_recommend(["Python", "SQL", "FastAPI"], [100, 100, 100]) is None
    assert reason_to_recommend(["Python", "SQL"], [30, 0]) == "You're learning Python"
    assert reason_to_recommend(["A", "B", "C", "D"], [100, 100, 100, 0]) == "You finished A and B and 1 more"
    assert reason_to_recommend(["Python", "SQL"], [0, 0]) is None


# --- the service ----------------------------------------------------------------------------------------------


def course(cid, title, percent):
    return Course(id=cid, title=title, world="w", description="", language="python", total_xp=1, modules=[], progress_percent=percent)


class FakeLearning:
    def __init__(self, percents):
        self.percents = percents

    async def list_courses(self, user_id):
        return [course(cid, cid.split("-", 1)[1].title(), p) for cid, p in self.percents.items()]


class FakeEnrollments:
    def __init__(self):
        self.enrolled: set[str] = set()

    async def ids(self, user_id):
        return set(self.enrolled)

    async def add(self, user_id, path_id, at):
        self.enrolled.add(path_id)

    async def remove(self, user_id, path_id):
        self.enrolled.discard(path_id)


ALL = {step: 0 for p in PATHS for step in p.steps}


def service(**percents):
    return PathService(FakeLearning({**ALL, **{k.replace("_", "-"): v for k, v in percents.items()}}), FakeEnrollments())


async def test_with_no_progress_nothing_is_suggested_and_every_path_is_listed():
    paths = await service().list("u")
    assert len(paths) == len(PATHS) and not any(p.recommended for p in paths)


async def test_finishing_python_suggests_the_paths_that_build_on_it_first():
    paths = await service(live_python=100).list("u")
    suggested = [p.id for p in paths if p.recommended]
    assert set(suggested) == {p.id for p in PATHS if "live-python" in p.steps}
    assert [p.id for p in paths[: len(suggested)]] == suggested
    ai = next(p for p in paths if p.id == "ai-ml")
    assert ai.reason == "You finished Python" and ai.completed_steps == 1 and ai.total_steps == 4


async def test_a_path_shows_each_course_with_what_is_done_and_what_comes_next():
    detail = await service(live_python=100, live_sql=45).get("u", "backend-python")
    assert [(s.course.id, s.state) for s in detail.steps] == [
        ("live-python", "completed"),
        ("live-sql", "in_progress"),
        ("fw-fastapi", "available"),
    ]
    assert detail.progress_percent == 48


async def test_choosing_and_leaving_a_path_is_remembered_and_listed_first():
    svc = service()
    assert (await svc.enroll("u", "mobile")).enrolled
    assert (await svc.list("u"))[0].id == "mobile"
    assert not (await svc.leave("u", "mobile")).enrolled


async def test_unknown_paths_and_paths_whose_courses_cannot_load_are_not_found():
    svc = service()
    with pytest.raises(NotFoundError):
        await svc.get("u", "nope")
    with pytest.raises(NotFoundError):
        await svc.enroll("u", "nope")
    thin = PathService(FakeLearning({"live-kotlin": 0}), FakeEnrollments())
    assert all(p.id != "mobile" for p in await thin.list("u"))
    with pytest.raises(NotFoundError):
        await thin.get("u", "mobile")
