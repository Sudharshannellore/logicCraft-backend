from datetime import datetime

from app.db import collections as c
from app.repositories.base import Repository


class PathEnrollmentRepository(Repository):
    """The career paths a player chose to follow. One small document per (player, path)."""

    collection_name = c.PATH_ENROLLMENTS

    @staticmethod
    def _key(user_id: str, path_id: str) -> str:
        return f"{user_id}:{path_id}"

    async def ids(self, user_id: str) -> set[str]:
        return {d["path_id"] async for d in self.col.find({"user_id": user_id}, {"path_id": 1})}

    async def add(self, user_id: str, path_id: str, at: datetime) -> None:
        await self.col.update_one(
            {"_id": self._key(user_id, path_id)},
            {"$setOnInsert": {"user_id": user_id, "path_id": path_id, "started_at": at}},
            upsert=True,
        )

    async def remove(self, user_id: str, path_id: str) -> None:
        await self.col.delete_one({"_id": self._key(user_id, path_id)})
