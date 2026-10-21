from datetime import datetime
from typing import Any

from pymongo import ReturnDocument

from app.db import collections as c
from app.repositories.base import Repository


class QuizAttemptRepository(Repository):
    """One document per player per quiz: best score, tries, and (for timed quizzes) the running clock."""

    collection_name = c.QUIZ_ATTEMPTS

    @staticmethod
    def _key(user_id: str, quiz_id: str) -> str:
        return f"{user_id}:{quiz_id}"

    async def get(self, user_id: str, quiz_id: str) -> dict[str, Any] | None:
        return await self.col.find_one({"_id": self._key(user_id, quiz_id)})

    async def start(
        self, user_id: str, quiz_id: str, *, course_id: str, kind: str, now: datetime, deadline: datetime
    ) -> dict[str, Any]:
        """Starts (or restarts) the clock; `tries` counts runs, and a new run forgets the last one's end."""
        doc = await self.col.find_one_and_update(
            {"_id": self._key(user_id, quiz_id)},
            {
                "$set": {"started_at": now, "deadline": deadline},
                "$unset": {"finished_at": ""},
                "$inc": {"tries": 1},
                "$setOnInsert": {"user_id": user_id, "quiz_id": quiz_id, "course_id": course_id, "kind": kind},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc

    async def finish(
        self,
        user_id: str,
        quiz_id: str,
        *,
        course_id: str,
        kind: str,
        lesson_id: str | None,
        percent: int | None,
        passed: bool,
        now: datetime,
        seconds: int | None,
    ) -> bool:
        """Records a graded run. Returns True when this run is the first pass (the one that pays)."""
        key = self._key(user_id, quiz_id)
        base: dict[str, Any] = {"user_id": user_id, "quiz_id": quiz_id, "course_id": course_id, "kind": kind}
        if lesson_id:
            base["lesson_id"] = lesson_id
        update: dict[str, Any] = {"$set": {"finished_at": now}, "$setOnInsert": base}
        if percent is not None:
            update["$max"] = {"best_percent": percent}
        await self.col.update_one({"_id": key}, update, upsert=True)
        if kind == "practice":  # untimed quizzes have no `start`, so count the run here
            await self.col.update_one({"_id": key}, {"$inc": {"tries": 1}})
        if not passed:
            return False
        first = await self.col.update_one(
            {"_id": key, "passed_at": {"$exists": False}}, {"$set": {"passed_at": now, "seconds": seconds}}
        )
        return first.modified_count == 1

    async def mark_timed_out(self, user_id: str, quiz_id: str, now: datetime) -> None:
        await self.col.update_one({"_id": self._key(user_id, quiz_id)}, {"$set": {"finished_at": now}})

    async def practice_for_course(self, user_id: str, course_id: str) -> dict[str, dict[str, Any]]:
        """{lesson_id: attempt} for the player's practice quizzes in one framework."""
        cursor = self.col.find({"user_id": user_id, "course_id": course_id, "kind": "practice"})
        return {d["lesson_id"]: d async for d in cursor if d.get("lesson_id")}

    async def solved_counts(self, user_id: str) -> dict[str, int]:
        """{course_id: practice quizzes passed}."""
        pipeline = [
            {"$match": {"user_id": user_id, "kind": "practice", "passed_at": {"$exists": True}}},
            {"$group": {"_id": "$course_id", "n": {"$sum": 1}}},
        ]
        cursor = await self.col.aggregate(pipeline)
        return {d["_id"]: d["n"] async for d in cursor}
