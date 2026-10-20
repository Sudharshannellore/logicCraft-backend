from typing import Any

from app.core.clock import utcnow
from app.db import collections as c
from app.repositories.base import Repository


class TutorialCacheRepository(Repository):
    """Cached provider responses. A TTL index on `created_at` expires them."""

    collection_name = c.TUTORIAL_CACHE

    async def get(self, key: str) -> Any | None:
        doc = await self.col.find_one({"_id": key})
        return doc["payload"] if doc else None

    async def put(self, key: str, payload: Any) -> None:
        await self.col.replace_one({"_id": key}, {"payload": payload, "created_at": utcnow()}, upsert=True)
