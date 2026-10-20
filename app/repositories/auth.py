from datetime import datetime

from pymongo import ReturnDocument

from app.db import collections as c
from app.repositories.base import Repository, from_doc, to_doc
from app.schemas.auth import RefreshTokenDoc


class RefreshTokenRepository(Repository):
    """Refresh tokens by SHA-256. A TTL index on `expires_at` removes expired ones."""

    collection_name = c.REFRESH_TOKENS

    async def insert(self, token: RefreshTokenDoc) -> None:
        await self.col.insert_one(to_doc(token))

    async def take(self, token_hash: str, now: datetime) -> RefreshTokenDoc | None:
        """Atomically removes and returns a live token — each refresh token works exactly once."""
        doc = await self.col.find_one_and_delete({"_id": token_hash, "expires_at": {"$gt": now}})
        return RefreshTokenDoc.model_validate(from_doc(doc)) if doc else None

    async def delete(self, token_hash: str) -> None:
        await self.col.delete_one({"_id": token_hash})

    async def delete_for_user(self, user_id: str) -> None:
        await self.col.delete_many({"user_id": user_id})


class LoginFailureRepository(Repository):
    """Failed logins per email. The TTL index on `first_at` ends a lockout window automatically."""

    collection_name = c.LOGIN_FAILURES

    async def count(self, email: str) -> int:
        doc = await self.col.find_one({"_id": email})
        return doc["count"] if doc else 0

    async def record(self, email: str, now: datetime) -> int:
        doc = await self.col.find_one_and_update(
            {"_id": email},
            {"$inc": {"count": 1}, "$setOnInsert": {"first_at": now}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["count"]

    async def clear(self, email: str) -> None:
        await self.col.delete_one({"_id": email})
