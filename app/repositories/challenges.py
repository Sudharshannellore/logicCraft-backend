from datetime import datetime
from typing import Any

from pymongo import ASCENDING, ReturnDocument

from app.db import collections as c
from app.repositories.base import Repository


class ChallengeAttemptRepository(Repository):
    """One document per player per challenge: when their clock started, which stages they cleared, their time."""

    collection_name = c.CHALLENGE_ATTEMPTS

    @staticmethod
    def _key(user_id: str, challenge_id: str) -> str:
        return f"{user_id}:{challenge_id}"

    async def get(self, user_id: str, challenge_id: str) -> dict[str, Any] | None:
        return await self.col.find_one({"_id": self._key(user_id, challenge_id)})

    async def start(self, user_id: str, challenge_id: str, now: datetime, deadline: datetime) -> dict[str, Any]:
        """Starts the clock, or returns the attempt already running."""
        return await self.col.find_one_and_update(
            {"_id": self._key(user_id, challenge_id)},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "challenge_id": challenge_id,
                    "started_at": now,
                    "deadline": deadline,
                    "cleared": [],
                    "tries": 1,
                    "won_at": None,
                    "seconds": None,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    async def restart(self, user_id: str, challenge_id: str, now: datetime, deadline: datetime) -> dict[str, Any]:
        return await self.col.find_one_and_update(
            {"_id": self._key(user_id, challenge_id), "won_at": None},
            {"$set": {"started_at": now, "deadline": deadline, "cleared": []}, "$inc": {"tries": 1}},
            return_document=ReturnDocument.AFTER,
        )

    async def clear_stage(self, user_id: str, challenge_id: str, slug: str, now: datetime) -> dict[str, Any] | None:
        """Records a cleared stage — only while the clock is still running."""
        return await self.col.find_one_and_update(
            {"_id": self._key(user_id, challenge_id), "won_at": None, "deadline": {"$gt": now}},
            {"$addToSet": {"cleared": slug}},
            return_document=ReturnDocument.AFTER,
        )

    async def mark_won(self, user_id: str, challenge_id: str, now: datetime, seconds: int) -> bool:
        """True the first time only."""
        result = await self.col.update_one(
            {"_id": self._key(user_id, challenge_id), "won_at": None},
            {"$set": {"won_at": now, "seconds": seconds}},
        )
        return result.modified_count == 1

    async def counts(self, challenge_id: str) -> tuple[int, int]:
        """(players who started, players who won)."""
        started = await self.col.count_documents({"challenge_id": challenge_id})
        won = await self.col.count_documents({"challenge_id": challenge_id, "won_at": {"$ne": None}})
        return started, won

    async def fastest(self, challenge_id: str, limit: int) -> list[dict[str, Any]]:
        cursor = (
            self.col.find({"challenge_id": challenge_id, "won_at": {"$ne": None}})
            .sort([("seconds", ASCENDING), ("won_at", ASCENDING)])
            .limit(limit)
        )
        return [d async for d in cursor]
