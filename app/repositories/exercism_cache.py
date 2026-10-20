from datetime import timedelta
from typing import Any

from app.core.clock import utcnow
from app.db import collections as c
from app.repositories.base import Repository


class ExercismCacheRepository(Repository):
    """Exercism track lists and exercise files. Each entry carries its own expiry (TTL index on `expires_at`)."""

    collection_name = c.EXERCISM_CACHE

    async def get(self, key: str) -> Any | None:
        doc = await self.col.find_one({"_id": key, "expires_at": {"$gt": utcnow()}})
        return doc["payload"] if doc else None

    async def put(self, key: str, payload: Any, *, ttl_seconds: int) -> None:
        await self.col.replace_one(
            {"_id": key}, {"payload": payload, "expires_at": utcnow() + timedelta(seconds=ttl_seconds)}, upsert=True
        )
