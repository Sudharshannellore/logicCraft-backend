"""Catalog repositories: static content loaded by the seeder."""

from app.db import collections as c
from app.repositories.base import CatalogRepository
from app.schemas.gamification import AchievementDef, QuestTemplate
from app.schemas.learning import Course, CoursePath, Lesson
from app.schemas.practice import Problem
from app.schemas.resumes import ResumeTemplate
from app.schemas.sql import SqlProblem, SqlTable
from app.schemas.store import XpPack, XpPlan
from app.schemas.wallet import StreakMilestone


class CourseRepository(CatalogRepository[Course]):
    collection_name = c.COURSES
    model = Course


class CoursePathRepository(CatalogRepository[CoursePath]):
    """Documents are keyed by course id."""

    collection_name = c.COURSE_PATHS
    model = CoursePath

    async def for_course(self, course_id: str) -> CoursePath | None:
        return await self.find_one({"course_id": course_id})


class LessonRepository(CatalogRepository[Lesson]):
    collection_name = c.LESSONS
    model = Lesson


class ProblemRepository(CatalogRepository[Problem]):
    collection_name = c.PROBLEMS
    model = Problem

    async def by_slug(self, slug: str) -> Problem | None:
        return await self.find_one({"slug": slug})


class SqlTableRepository(CatalogRepository[SqlTable]):
    collection_name = c.SQL_TABLES
    model = SqlTable


class SqlProblemRepository(CatalogRepository[SqlProblem]):
    collection_name = c.SQL_PROBLEMS
    model = SqlProblem

    async def by_slug(self, slug: str) -> SqlProblem | None:
        return await self.find_one({"slug": slug})


class QuestTemplateRepository(CatalogRepository[QuestTemplate]):
    collection_name = c.QUEST_TEMPLATES
    model = QuestTemplate


class AchievementRepository(CatalogRepository[AchievementDef]):
    collection_name = c.ACHIEVEMENTS
    model = AchievementDef


class ResumeTemplateRepository(CatalogRepository[ResumeTemplate]):
    collection_name = c.RESUME_TEMPLATES
    model = ResumeTemplate


class XpPlanRepository(CatalogRepository[XpPlan]):
    collection_name = c.XP_PLANS
    model = XpPlan


class XpPackRepository(CatalogRepository[XpPack]):
    collection_name = c.XP_PACKS
    model = XpPack


class StreakMilestoneRepository(CatalogRepository[StreakMilestone]):
    collection_name = c.STREAK_MILESTONES
    model = StreakMilestone
