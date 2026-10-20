"""Loads the course catalog: one module per course in `app/seed/data/courses/`.

Each module defines three things:

    COURSE  = {"id", "title", "world", "description", "language", "modules": [{"id", "title"}]}
    ZONES   = [{"id", "name", "tagline", "difficulty",
                "nodes": [{"id", "title", "difficulty", "xp_reward", "estimated_minutes"}],
                "boss": {"id", "name", "sprite", "challenge", "stages", "xp_reward"}}]
    LESSONS = [{"id", "module_id", "title", "concept", "explanation", "code_example",
                "code_walkthrough", "key_points", "analogy", "quiz", "try_it"?}]

Everything derivable is derived here — a node opens the lesson with its id, lessons get the course
id, module lesson/exercise counts and the course's total XP are counted — and every cross-reference
is checked, so a typo fails the seed instead of shipping a broken map.
"""

import importlib
import re
from dataclasses import dataclass
from typing import Any

from app.domain.languages import LANGUAGES
from app.seed.data.courses import COURSE_ORDER


class CourseContentError(ValueError):
    pass


@dataclass(frozen=True)
class CourseCatalog:
    courses: list[dict[str, Any]]
    paths: list[dict[str, Any]]
    lessons: list[dict[str, Any]]


def _check(condition: bool, course_id: str, message: str) -> None:
    if not condition:
        raise CourseContentError(f"[{course_id}] {message}")


def build_course(module_name: str, seen_ids: set[str]) -> tuple[dict, dict, list[dict]]:
    module = importlib.import_module(f"app.seed.data.courses.{module_name}")
    course, zones, lessons = dict(module.COURSE), module.ZONES, module.LESSONS
    cid = course["id"]

    _check(course["language"] in LANGUAGES, cid, f"unknown language {course['language']!r}")
    _check(len(zones) > 0, cid, "a course needs at least one zone")

    module_ids = [m["id"] for m in course["modules"]]
    _check(len(module_ids) == len(set(module_ids)), cid, "module ids must be unique")
    lessons_by_id = {}
    for lesson in lessons:
        lid = lesson["id"]
        _check(lid not in lessons_by_id, cid, f"duplicate lesson {lid}")
        _check(lesson["module_id"] in module_ids, cid, f"lesson {lid} uses unknown module {lesson['module_id']}")
        quiz = lesson["quiz"]
        _check(0 <= quiz["correct_index"] < len(quiz["options"]), cid, f"lesson {lid}: quiz answer out of range")
        _check(len(set(quiz["options"])) == len(quiz["options"]), cid, f"lesson {lid}: duplicate quiz options")
        for check in (lesson.get("try_it") or {}).get("checks", []):
            try:
                re.compile(check["pattern"])
            except re.error as exc:
                raise CourseContentError(f"[{cid}] lesson {lid}: bad try-it pattern ({exc})") from exc
        lessons_by_id[lid] = lesson

    node_ids: list[str] = []
    path_zones = []
    for zone in zones:
        nodes = [{**node, "lesson_id": node["id"]} for node in zone["nodes"]]
        node_ids += [n["id"] for n in nodes]
        path_zones.append({**zone, "nodes": nodes})
        for key in (zone["id"], zone["boss"]["id"], *(n["id"] for n in nodes)):
            _check(key not in seen_ids, cid, f"id {key!r} is already used by another course")
            seen_ids.add(key)

    _check(len(node_ids) == len(set(node_ids)), cid, "duplicate topic ids on the map")
    missing = [n for n in node_ids if n not in lessons_by_id]
    _check(not missing, cid, f"topics without a lesson: {', '.join(missing)}")
    unused = [lid for lid in lessons_by_id if lid not in node_ids]
    _check(not unused, cid, f"lessons not on the map: {', '.join(unused)}")

    course["modules"] = [
        {
            **m,
            "lessons_count": sum(1 for lesson in lessons if lesson["module_id"] == m["id"]),
            "exercises_count": sum(1 for lesson in lessons if lesson["module_id"] == m["id"] and lesson.get("try_it")),
        }
        for m in course["modules"]
    ]
    course["total_xp"] = sum(n["xp_reward"] for z in zones for n in z["nodes"]) + sum(
        z["boss"]["xp_reward"] for z in zones
    )
    return course, {"course_id": cid, "zones": path_zones}, [{**lesson, "course_id": cid} for lesson in lessons]


def load_courses() -> CourseCatalog:
    courses, paths, lessons = [], [], []
    seen_ids: set[str] = set()
    for name in COURSE_ORDER:
        course, path, course_lessons = build_course(name, seen_ids)
        _check(course["id"] not in {c["id"] for c in courses}, course["id"], "duplicate course id")
        courses.append(course)
        paths.append(path)
        lessons += course_lessons
    return CourseCatalog(courses=courses, paths=paths, lessons=lessons)
