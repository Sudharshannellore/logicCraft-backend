from datetime import datetime

from pymongo.errors import DuplicateKeyError

from app.db import collections as c
from app.repositories.base import Repository, from_doc, to_doc
from app.schemas.wallet import LedgerEntry


class LedgerRepository(Repository):
    """Append-only record of every XP movement. Also the source for activity and period leaderboards."""

    collection_name = c.XP_LEDGER

    async def insert(self, entry: LedgerEntry) -> bool:
        """False when `reward_key` was already paid to this user (unique index)."""
        try:
            await self.col.insert_one(to_doc(entry))
        except DuplicateKeyError:
            return False
        return True

    async def insert_many(self, entries: list[LedgerEntry]) -> None:
        if entries:
            await self.col.insert_many([to_doc(e) for e in entries])

    async def delete(self, entry_id: str) -> None:
        await self.col.delete_one({"_id": entry_id})

    async def for_user(self, user_id: str, *, limit: int = 50) -> list[LedgerEntry]:
        cursor = self.col.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        return [LedgerEntry.model_validate(from_doc(d)) async for d in cursor]

    async def reward_keys(self, user_id: str) -> list[str]:
        return await self.col.distinct("reward_key", {"user_id": user_id, "reward_key": {"$type": "string"}})

    async def has_reward(self, user_id: str, reward_key: str) -> bool:
        return await self.col.count_documents({"user_id": user_id, "reward_key": reward_key}, limit=1) > 0

    async def recent_activity(self, *, limit: int) -> list[LedgerEntry]:
        cursor = self.col.find({"kind": "earn", "activity": {"$type": "string"}}).sort("created_at", -1).limit(limit)
        return [LedgerEntry.model_validate(from_doc(d)) async for d in cursor]

    async def earned_since(self, since: datetime, *, user_ids: list[str] | None = None, limit: int = 50) -> list[dict]:
        """[{user_id, xp}] — XP earned since `since`, highest first."""
        match: dict = {"kind": "earn", "created_at": {"$gte": since}}
        if user_ids is not None:
            match["user_id"] = {"$in": user_ids}
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$user_id", "xp": {"$sum": "$amount"}}},
            {"$sort": {"xp": -1}},
            {"$limit": limit},
        ]
        cursor = await self.col.aggregate(pipeline)
        return [{"user_id": d["_id"], "xp": d["xp"]} async for d in cursor]
