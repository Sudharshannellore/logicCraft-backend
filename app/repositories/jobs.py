from datetime import datetime
from typing import Any

from pymongo import DESCENDING, UpdateOne

from app.db import collections as c
from app.integrations.jobs.boards import JobPosting
from app.repositories.base import Repository


class JobListingRepository(Repository):
    """Live listings from the job boards. Each expires on its own (TTL index on `expires_at`)."""

    collection_name = c.JOB_LISTINGS

    async def upsert_many(self, postings: list[JobPosting], *, keep_until: datetime) -> None:
        if not postings:
            return
        ops = []
        for posting in postings:
            doc = posting.to_doc()
            job_id = doc.pop("_id")
            languages = doc.pop("languages")
            ends = posting.expires_at
            doc["expires_at"] = min(ends, keep_until) if ends else keep_until
            ops.append(
                UpdateOne(
                    {"_id": job_id},
                    {"$set": doc, "$addToSet": {"languages": {"$each": languages}}},
                    upsert=True,
                )
            )
        await self.col.bulk_write(ops, ordered=False)

    async def search(self, filters: dict[str, Any], *, limit: int) -> list[dict[str, Any]]:
        cursor = self.col.find(filters).sort("posted_at", DESCENDING).limit(limit)
        return [d async for d in cursor]

    async def get(self, job_id: str) -> dict[str, Any] | None:
        return await self.col.find_one({"_id": job_id})


class JobFeedRepository(Repository):
    """When each board's feed for each language was last fetched, so boards are asked a few times a day at most."""

    collection_name = c.JOB_FEEDS

    async def all(self) -> dict[str, dict[str, Any]]:
        return {d["_id"]: d async for d in self.col.find({})}

    async def record(self, key: str, *, attempted_at: datetime, ok: bool, count: int) -> None:
        update: dict[str, Any] = {"attempted_at": attempted_at, "ok": ok}
        if ok:
            update |= {"fetched_at": attempted_at, "count": count}
        await self.col.update_one({"_id": key}, {"$set": update}, upsert=True)
