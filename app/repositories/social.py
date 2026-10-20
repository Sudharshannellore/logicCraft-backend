from datetime import datetime
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.db import collections as c
from app.repositories.base import Repository, from_doc, to_doc
from app.schemas.social import DuelDoc, FriendRequestDoc


class FriendRequestRepository(Repository):
    collection_name = c.FRIEND_REQUESTS

    async def create(self, request: FriendRequestDoc) -> bool:
        try:
            await self.col.insert_one(to_doc(request))
        except DuplicateKeyError:
            return False
        return True

    async def pending(self, *, from_id: str | None = None, to_id: str | None = None) -> list[FriendRequestDoc]:
        query: dict[str, Any] = {"status": "pending"}
        if from_id:
            query["from_id"] = from_id
        if to_id:
            query["to_id"] = to_id
        cursor = self.col.find(query).sort("created_at", -1)
        return [FriendRequestDoc.model_validate(from_doc(d)) async for d in cursor]

    async def resolve(self, from_id: str, to_id: str, status: str, now: datetime) -> bool:
        result = await self.col.update_one(
            {"from_id": from_id, "to_id": to_id, "status": "pending"},
            {"$set": {"status": status, "resolved_at": now}},
        )
        return result.modified_count == 1


class FriendshipRepository(Repository):
    """One document per pair of friends, keyed by the sorted pair."""

    collection_name = c.FRIENDSHIPS

    @staticmethod
    def _key(a: str, b: str) -> str:
        return ":".join(sorted((a, b)))

    async def friend_ids(self, user_id: str) -> list[str]:
        cursor = self.col.find({"users": user_id}).sort("created_at", 1)
        return [next(u for u in d["users"] if u != user_id) async for d in cursor]

    async def are_friends(self, a: str, b: str) -> bool:
        return await self.col.count_documents({"_id": self._key(a, b)}, limit=1) > 0

    async def add(self, a: str, b: str, now: datetime) -> None:
        await self.col.update_one(
            {"_id": self._key(a, b)}, {"$setOnInsert": {"users": [a, b], "created_at": now}}, upsert=True
        )

    async def remove(self, a: str, b: str) -> bool:
        result = await self.col.delete_one({"_id": self._key(a, b)})
        return result.deleted_count == 1


class DuelRepository(Repository):
    collection_name = c.DUELS

    async def insert(self, duel: DuelDoc) -> None:
        await self.col.insert_one(to_doc(duel))

    async def get(self, duel_id: str) -> DuelDoc | None:
        doc = await self.col.find_one({"_id": duel_id})
        return DuelDoc.model_validate(from_doc(doc)) if doc else None

    async def for_user(self, user_id: str, *, limit: int = 40) -> list[DuelDoc]:
        cursor = (
            self.col.find({"$or": [{"challenger_id": user_id}, {"opponent_id": user_id}]})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [DuelDoc.model_validate(from_doc(d)) async for d in cursor]

    async def open_duels(self) -> list[DuelDoc]:
        cursor = self.col.find({"status": {"$in": ["pending", "active"]}})
        return [DuelDoc.model_validate(from_doc(d)) async for d in cursor]

    async def transition(self, duel_id: str, from_status: str, fields: dict[str, Any]) -> DuelDoc | None:
        """Compare-and-set on status, so two concurrent actions can't both apply."""
        doc = await self.col.find_one_and_update(
            {"_id": duel_id, "status": from_status}, {"$set": fields}, return_document=ReturnDocument.AFTER
        )
        return DuelDoc.model_validate(from_doc(doc)) if doc else None

    async def set_player_fields(
        self, duel_id: str, user_id: str, fields: dict[str, Any], *, only_if_unset: str | None = None
    ) -> DuelDoc | None:
        query: dict[str, Any] = {"_id": duel_id, "status": "active"}
        if only_if_unset:
            query[f"players.{user_id}.{only_if_unset}"] = None
        doc = await self.col.find_one_and_update(
            query,
            {"$set": {f"players.{user_id}.{k}": v for k, v in fields.items()}},
            return_document=ReturnDocument.AFTER,
        )
        return DuelDoc.model_validate(from_doc(doc)) if doc else None

    async def claim_settlement(self, duel_id: str, winner_id: str | None) -> DuelDoc | None:
        doc = await self.col.find_one_and_update(
            {"_id": duel_id, "settled": False},
            {"$set": {"settled": True, "status": "finished", "winner_id": winner_id}},
            return_document=ReturnDocument.AFTER,
        )
        return DuelDoc.model_validate(from_doc(doc)) if doc else None
