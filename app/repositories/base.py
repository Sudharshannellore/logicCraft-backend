import time
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


# Catalog content only changes when the seeder runs, so reads are kept in memory for a few minutes:
# every database round trip is expensive when the API and MongoDB are far apart. Raw documents are
# cached and validated on each read, so callers always get their own fresh model objects.
CATALOG_TTL_SECONDS = 300
_catalog_cache: dict[tuple, tuple[float, Any]] = {}


def clear_catalog_cache() -> None:
    _catalog_cache.clear()


class CatalogRepository[M: BaseModel](Repository):
    """Read-only access to a catalog collection, ordered by its seed position."""

    model: type[M]

    async def _cached(self, key: tuple, load):
        full_key = (self.collection_name, *key)
        hit = _catalog_cache.get(full_key)
        now = time.monotonic()
        if hit and now - hit[0] < CATALOG_TTL_SECONDS:
            return hit[1]
        value = await load()
        _catalog_cache[full_key] = (now, value)
        return value

    async def list(self, filters: dict[str, Any] | None = None) -> list[M]:
        async def load():
            return [d async for d in self.col.find(filters or {}).sort("position", 1)]

        docs = await self._cached(("list", repr(sorted((filters or {}).items()))), load)
        return [self.model.model_validate(from_doc(d)) for d in docs]

    async def get(self, item_id: str) -> M | None:
        doc = await self._cached(("get", item_id), lambda: self.col.find_one({"_id": item_id}))
        return self.model.model_validate(from_doc(doc)) if doc else None

    async def find_one(self, filters: dict[str, Any]) -> M | None:
        doc = await self._cached(("find", repr(sorted(filters.items()))), lambda: self.col.find_one(filters))
        return self.model.model_validate(from_doc(doc)) if doc else None
