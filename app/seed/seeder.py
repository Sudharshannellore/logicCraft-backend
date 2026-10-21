"""Loads catalog content (courses, problems, quests, plans…) into MongoDB.

Catalog collections are validated through the API models, then replaced wholesale, so
re-seeding picks up content edits. There is no demo data: players and everything they do
come only from real sign-ups.
"""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase

from app.db import collections as c
from app.repositories.base import clear_catalog_cache
from app.schemas.gamification import AchievementDef, QuestTemplate
from app.schemas.learning import Course, CoursePath, Lesson
from app.schemas.practice import Problem
from app.schemas.resumes import ResumeTemplate
from app.schemas.sql import SqlProblem, SqlTable
from app.schemas.store import XpPack, XpPlan
from app.schemas.wallet import StreakMilestone
from app.seed.courses import load_courses

logger = logging.getLogger(__name__)
DATA = Path(__file__).parent / "data"


def _load(name: str) -> dict[str, Any]:
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def _catalog_docs(model: type[BaseModel], items: list[dict], key: str = "id") -> list[dict]:
    """Validate each item through its API model, then store it snake_case with `_id` and a stable `position`."""
    docs = []
    for position, item in enumerate(items):
        data = model.model_validate(item).model_dump(mode="python")
        docs.append({**data, "_id": str(data[key]), "position": position})
    return docs


def catalog() -> dict[str, list[dict]]:
    problems, sql, game, store = (_load(n) for n in ("problems", "sql", "gamification", "store"))
    courses = load_courses()
    return {
        c.COURSES: _catalog_docs(Course, courses.courses),
        c.COURSE_PATHS: _catalog_docs(CoursePath, courses.paths, key="course_id"),
        c.LESSONS: _catalog_docs(Lesson, courses.lessons),
        c.PROBLEMS: _catalog_docs(Problem, problems["problems"]),
        c.SQL_TABLES: _catalog_docs(SqlTable, sql["tables"], key="name"),
        c.SQL_PROBLEMS: _catalog_docs(SqlProblem, sql["problems"]),
        c.QUEST_TEMPLATES: _catalog_docs(QuestTemplate, game["questTemplates"]),
        c.ACHIEVEMENTS: _catalog_docs(AchievementDef, game["achievements"]),
        c.STREAK_MILESTONES: _catalog_docs(StreakMilestone, game["streakMilestones"], key="days"),
        c.RESUME_TEMPLATES: _catalog_docs(ResumeTemplate, store["resumeTemplates"]),
        c.XP_PLANS: _catalog_docs(XpPlan, store["xpPlans"]),
        c.XP_PACKS: _catalog_docs(XpPack, store["xpPacks"]),
    }


async def seed_catalog(db: AsyncDatabase) -> None:
    for name, docs in catalog().items():
        await db[name].delete_many({})
        if docs:
            await db[name].insert_many(docs)
    clear_catalog_cache()


async def seed_if_empty(db: AsyncDatabase) -> bool:
    """Loads the catalog on first start. Returns True when it did. Players only come from real sign-ups."""
    if await db[c.COURSES].estimated_document_count() > 0:
        return False
    await seed_catalog(db)
    return True
