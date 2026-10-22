from typing import Any

from pymongo import ReturnDocument

from app.db import collections as c
from app.repositories.base import Repository, from_doc, to_doc
from app.schemas.users import StreakState, UserDoc


class UserRepository(Repository):
    collection_name = c.USERS

    async def get(self, user_id: str) -> UserDoc | None:
        doc = await self.col.find_one({"_id": user_id})
        return UserDoc.model_validate(from_doc(doc)) if doc else None

    async def get_by_email(self, email: str) -> UserDoc | None:
        doc = await self.col.find_one({"email": email.lower()})
        return UserDoc.model_validate(from_doc(doc)) if doc else None

    async def email_taken(self, email: str) -> bool:
        return await self.col.count_documents({"email": email.lower()}, limit=1) > 0

    async def set_password(self, user_id: str, password_hash: str, *, revoke_sessions: bool) -> None:
        update: dict[str, Any] = {"$set": {"password_hash": password_hash}}
        if revoke_sessions:
            update["$inc"] = {"token_version": 1}
        await self.col.update_one({"_id": user_id}, update)

    async def get_many(self, user_ids: list[str]) -> list[UserDoc]:
        cursor = self.col.find({"_id": {"$in": user_ids}})
        return [UserDoc.model_validate(from_doc(d)) async for d in cursor]

    async def totals(self) -> dict[str, int]:
        """Platform-wide counts: players, problems solved and bosses defeated."""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "learners": {"$sum": 1},
                    "problems_solved": {"$sum": {"$add": ["$stats.code_solved", "$stats.sql_solved"]}},
                    "bosses_defeated": {"$sum": "$stats.bosses_defeated"},
                }
            }
        ]
        rows = await (await self.col.aggregate(pipeline)).to_list(1)
        row = rows[0] if rows else {}
        return {k: int(row.get(k) or 0) for k in ("learners", "problems_solved", "bosses_defeated")}

    async def top_by_xp(self, *, limit: int = 100) -> list[UserDoc]:
        cursor = self.col.find({}).sort("wallet.xp", -1).limit(limit)
        return [UserDoc.model_validate(from_doc(d)) async for d in cursor]

    async def insert(self, user: UserDoc) -> None:
        await self.col.insert_one(to_doc(user))

    async def set_fields(self, user_id: str, fields: dict[str, Any]) -> UserDoc | None:
        doc = await self.col.find_one_and_update(
            {"_id": user_id}, {"$set": fields}, return_document=ReturnDocument.AFTER
        )
        return UserDoc.model_validate(from_doc(doc)) if doc else None

    async def inc_field(self, user_id: str, field: str, amount: int) -> None:
        await self.col.update_one({"_id": user_id}, {"$inc": {field: amount}})

    async def add_to_set(self, user_id: str, field: str, value: Any) -> None:
        await self.col.update_one({"_id": user_id}, {"$addToSet": {field: value}})

    async def handle_taken(self, handle: str, *, excluding: str) -> bool:
        return await self.col.count_documents({"handle": handle, "_id": {"$ne": excluding}}, limit=1) > 0

    async def rank_of(self, lifetime_xp: int) -> int:
        """1-based global rank by total XP."""
        return await self.col.count_documents({"wallet.xp": {"$gt": lifetime_xp}}) + 1

    # --- Wallet (atomic) ------------------------------------------------------------

    async def add_xp(self, user_id: str, amount: int, *, lifetime: bool) -> UserDoc | None:
        inc = {"wallet.xp": amount, **({"wallet.lifetime_xp": amount} if lifetime else {})}
        doc = await self.col.find_one_and_update({"_id": user_id}, {"$inc": inc}, return_document=ReturnDocument.AFTER)
        return UserDoc.model_validate(from_doc(doc)) if doc else None

    async def try_spend_xp(self, user_id: str, amount: int) -> UserDoc | None:
        """Deducts `amount` only if the balance covers it. None = not enough XP."""
        doc = await self.col.find_one_and_update(
            {"_id": user_id, "wallet.xp": {"$gte": amount}},
            {"$inc": {"wallet.xp": -amount}},
            return_document=ReturnDocument.AFTER,
        )
        return UserDoc.model_validate(from_doc(doc)) if doc else None

    async def add_milestone_if_new(self, user_id: str, days: int) -> bool:
        result = await self.col.update_one(
            {"_id": user_id, "claimed_milestones": {"$ne": days}}, {"$push": {"claimed_milestones": days}}
        )
        return result.modified_count == 1

    # --- Stats, streak, achievements --------------------------------------------------

    async def inc_stats(self, user_id: str, deltas: dict[str, int]) -> None:
        if deltas:
            await self.col.update_one({"_id": user_id}, {"$inc": {f"stats.{k}": v for k, v in deltas.items()}})

    async def set_streak(self, user_id: str, streak: StreakState) -> None:
        await self.col.update_one({"_id": user_id}, {"$set": {"streak": streak.model_dump()}})

    async def unlock_achievements(self, user_id: str, unlocked: dict[str, Any]) -> None:
        if unlocked:
            await self.col.update_one(
                {"_id": user_id}, {"$set": {f"achievements.{key}": at for key, at in unlocked.items()}}
            )
