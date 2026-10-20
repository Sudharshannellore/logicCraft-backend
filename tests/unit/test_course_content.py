"""Every course module must load, validate through the API models and meet the content bar."""

import importlib
import pkgutil
import re

import pytest

import app.seed.data.courses as courses_pkg
from app.schemas.learning import Course, CoursePath, Lesson
from app.seed.courses import build_course, load_courses
from app.seed.data.courses import COURSE_ORDER

MODULES = sorted(m.name for m in pkgutil.iter_modules(courses_pkg.__path__))


def test_every_course_module_is_listed_in_course_order():
    assert sorted(COURSE_ORDER) == MODULES


def test_catalog_loads_with_ids_unique_across_courses():
    catalog = load_courses()
    lesson_ids = [lesson["id"] for lesson in catalog.lessons]
    assert len(lesson_ids) == len(set(lesson_ids))


@pytest.mark.parametrize("name", MODULES)
def test_course_content(name: str):
    module = importlib.import_module(f"app.seed.data.courses.{name}")
    course, path, lessons = build_course(name, set())
    Course.model_validate(course)
    CoursePath.model_validate(path)

    order = ["easy", "medium", "hard"]
    difficulties = [z["difficulty"] for z in module.ZONES]
    assert difficulties == sorted(difficulties, key=order.index), "zones should get harder"

    for raw in lessons:
        lesson = Lesson.model_validate(raw)
        where = f"{course['id']}/{lesson.id}"
        assert len(lesson.quiz.options) == 4, f"{where}: quiz needs 4 options"
        assert len(lesson.key_points or []) == 3, f"{where}: needs 3 key points"
        assert lesson.code_walkthrough, f"{where}: needs a code walkthrough"
        assert lesson.explanation.strip() and lesson.code_example.strip() and lesson.analogy, f"{where}: missing text"
        if lesson.try_it:
            starter = lesson.try_it.starter_code
            assert not all(re.search(c.pattern, starter) for c in lesson.try_it.checks), (
                f"{where}: the unchanged starter code already passes the Try it checks"
            )
