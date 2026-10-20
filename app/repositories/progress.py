from typing import Any

from pymongo import ReturnDocument

from app.db import collections as c
from app.repositories.base import Repository


class CourseProgressRepository(Repository):
    """Per player, per course: cleared topics and defeated zone bosses."""

    collection_name = c.COURSE_PROGRESS

    @staticmethod
    def _key(user_id: str, course_id: str) -> str:
        return f"{user_id}:{course_id}"

    async def get(self, user_id: str, course_id: str) -> dict[str, list[str]]:
        doc = await self.col.find_one({"_id": self._key(user_id, course_id)})
        return {
            "completed_nodes": (doc or {}).get("completed_nodes", []),
            "defeated_bosses": (doc or {}).get("defeated_bosses", []),
        }

    async def add(
        self, user_id: str, course_id: str, *, node_id: str | None = None, boss_id: str | None = None
    ) -> None:
        add: dict[str, Any] = {}
        if node_id:
            add["completed_nodes"] = node_id
        if boss_id:
            add["defeated_bosses"] = boss_id
        await self.col.update_one(
            {"_id": self._key(user_id, course_id)},
            {"$addToSet": add, "$setOnInsert": {"user_id": user_id, "course_id": course_id}},
            upsert=True,
        )


class DailyQuestRepository(Repository):
    """One document per player per day: which template, per-task progress, claimed flag."""

    collection_name = c.DAILY_QUESTS

    @staticmethod
    def _key(user_id: str, day: str) -> str:
        return f"{user_id}:{day}"

    async def get_or_create(self, user_id: str, day: str, template_id: str) -> dict[str, Any]:
        return await self.col.find_one_and_update(
            {"_id": self._key(user_id, day)},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "date": day,
                    "template_id": template_id,
                    "progress": {},
                    "claimed": False,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    async def increment(self, user_id: str, day: str, task_ids: list[str], amount: int) -> None:
        await self.col.update_one(
            {"_id": self._key(user_id, day)}, {"$inc": {f"progress.{t}": amount for t in task_ids}}
        )

    async def mark_claimed(self, user_id: str, day: str) -> bool:
        result = await self.col.update_one(
            {"_id": self._key(user_id, day), "claimed": False}, {"$set": {"claimed": True}}
        )
        return result.modified_count == 1

    async def unmark_claimed(self, user_id: str, day: str) -> None:
        await self.col.update_one({"_id": self._key(user_id, day)}, {"$set": {"claimed": False}})
