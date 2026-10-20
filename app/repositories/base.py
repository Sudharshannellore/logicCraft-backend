from typing import Any

from pydantic import BaseModel
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase


def to_doc(model: BaseModel) -> dict[str, Any]:
    """Model -> MongoDB document: snake_case fields, `id` stored as `_id`."""
    doc = model.model_dump(mode="python", by_alias=False)
    doc["_id"] = doc.pop("id")
    return doc


def from_doc(doc: dict[str, Any]) -> dict[str, Any]:
    doc = dict(doc)
    doc["id"] = doc.pop("_id")
    return doc


class Repository:
    collection_name: str

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.col: AsyncCollection = db[self.collection_name]


class CatalogRepository[M: BaseModel](Repository):
    """Read-only access to a catalog collection, ordered by its seed position."""

    model: type[M]

    async def list(self, filters: dict[str, Any] | None = None) -> list[M]:
        cursor = self.col.find(filters or {}).sort("position", 1)
        return [self.model.model_validate(from_doc(d)) async for d in cursor]

    async def get(self, item_id: str) -> M | None:
        doc = await self.col.find_one({"_id": item_id})
        return self.model.model_validate(from_doc(doc)) if doc else None

    async def find_one(self, filters: dict[str, Any]) -> M | None:
        doc = await self.col.find_one(filters)
        return self.model.model_validate(from_doc(doc)) if doc else None
