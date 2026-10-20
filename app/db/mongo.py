from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase


class Mongo:
    """Owns the MongoDB client for the app's lifetime."""

    def __init__(self, uri: str, db_name: str):
        self._client: AsyncMongoClient = AsyncMongoClient(uri, tz_aware=True, uuidRepresentation="standard")
        self.db: AsyncDatabase = self._client[db_name]

    async def ping(self) -> bool:
        await self._client.admin.command("ping")
        return True

    async def close(self) -> None:
        await self._client.close()
