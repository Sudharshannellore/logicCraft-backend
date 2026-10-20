"""Repositories for player-owned documents: subscriptions, purchases, resumes, job applications, submissions."""

from datetime import datetime
from typing import Any

from pymongo import ReturnDocument

from app.db import collections as c
from app.repositories.base import Repository, from_doc, to_doc
from app.schemas.jobs import JobApplicationDoc
from app.schemas.resumes import ResumeDoc
from app.schemas.store import PurchaseDoc, SubscriptionDoc


class SubscriptionRepository(Repository):
    collection_name = c.SUBSCRIPTIONS

    async def get(self, user_id: str) -> SubscriptionDoc | None:
        doc = await self.col.find_one({"_id": user_id})
        return SubscriptionDoc.model_validate({**doc, "user_id": doc["_id"]}) if doc else None

    async def save(self, sub: SubscriptionDoc) -> None:
        doc = sub.model_dump()
        await self.col.replace_one({"_id": doc.pop("user_id")}, doc, upsert=True)

    async def delete(self, user_id: str) -> None:
        await self.col.delete_one({"_id": user_id})


class PurchaseRepository(Repository):
    collection_name = c.PURCHASES

    async def insert(self, purchase: PurchaseDoc) -> None:
        await self.col.insert_one(to_doc(purchase))

    async def for_user(self, user_id: str, *, limit: int = 50) -> list[PurchaseDoc]:
        cursor = self.col.find({"user_id": user_id}).sort("at", -1).limit(limit)
        return [PurchaseDoc.model_validate(from_doc(d)) async for d in cursor]


class ResumeRepository(Repository):
    collection_name = c.RESUMES

    async def for_user(self, user_id: str) -> list[ResumeDoc]:
        cursor = self.col.find({"user_id": user_id}).sort("created_at", 1)
        return [ResumeDoc.model_validate(from_doc(d)) async for d in cursor]

    async def get(self, user_id: str, resume_id: str) -> ResumeDoc | None:
        doc = await self.col.find_one({"_id": resume_id, "user_id": user_id})
        return ResumeDoc.model_validate(from_doc(doc)) if doc else None

    async def count(self, user_id: str) -> int:
        return await self.col.count_documents({"user_id": user_id})

    async def insert(self, resume: ResumeDoc) -> None:
        await self.col.insert_one(to_doc(resume))

    async def update(self, user_id: str, resume_id: str, fields: dict[str, Any]) -> bool:
        result = await self.col.update_one({"_id": resume_id, "user_id": user_id}, {"$set": fields})
        return result.matched_count == 1

    async def delete(self, user_id: str, resume_id: str) -> bool:
        result = await self.col.delete_one({"_id": resume_id, "user_id": user_id})
        return result.deleted_count == 1


class JobApplicationRepository(Repository):
    collection_name = c.JOB_APPLICATIONS

    async def insert(self, application: JobApplicationDoc) -> None:
        await self.col.insert_one(to_doc(application))

    async def for_user(self, user_id: str) -> list[JobApplicationDoc]:
        cursor = self.col.find({"user_id": user_id}).sort("applied_at", -1)
        return [JobApplicationDoc.model_validate(from_doc(d)) async for d in cursor]

    async def find(self, user_id: str, job_id: str) -> JobApplicationDoc | None:
        doc = await self.col.find_one({"user_id": user_id, "job_id": job_id})
        return JobApplicationDoc.model_validate(from_doc(doc)) if doc else None

    async def set_status(
        self, user_id: str, application_id: str, status: str, now: datetime
    ) -> JobApplicationDoc | None:
        doc = await self.col.find_one_and_update(
            {"_id": application_id, "user_id": user_id},
            {"$set": {"status": status, "status_updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )
        return JobApplicationDoc.model_validate(from_doc(doc)) if doc else None


class SubmissionRepository(Repository):
    """Every code/SQL Submit, kept for history and acceptance stats."""

    collection_name = c.SUBMISSIONS

    async def insert(self, doc: dict[str, Any]) -> None:
        await self.col.insert_one(doc)

    async def solved_slugs(self, user_id: str, kind: str) -> set[str]:
        return set(await self.col.distinct("slug", {"user_id": user_id, "kind": kind, "passed": True}))
