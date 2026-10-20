"""API tests against a real MongoDB (a throwaway `codequest_test` database).

Point TEST_MONGODB_URI at a server (default mongodb://localhost:27017); the tests skip themselves when it isn't reachable.
External tutorial platforms are never called — providers are replaced with a stub.
"""

import os

import httpx
import pytest
from pymongo import AsyncMongoClient

from app.core.config import Settings
from app.main import create_app
from app.schemas.tutorials import TutorialResource

MONGODB_URI = os.getenv("TEST_MONGODB_URI", "mongodb://localhost:27017")
TEST_DB = "codequest_test"


class StubProvider:
    name = "stub"
    label = "Stub"
    homepage = "https://example.com"
    kinds = ["article"]
    requires_key = False
    enabled = True
    languages = None

    def supports(self, language):
        return True

    async def search(self, query, language, limit):
        return [
            TutorialResource(
                id="stub:1", provider="stub", kind="article", title=f"{query} tutorial", url="https://example.com/t"
            )
        ]


@pytest.fixture(scope="session")
async def mongo_available():
    client = AsyncMongoClient(MONGODB_URI, serverSelectionTimeoutMS=1500)
    try:
        await client.admin.command("ping")
    except Exception:
        pytest.skip(f"MongoDB not reachable at {MONGODB_URI}")
    finally:
        await client.close()


PASSWORD = "Learning2026"


async def register(http: httpx.AsyncClient, username: str, email: str, password: str = PASSWORD) -> dict[str, str]:
    """Signs a brand-new player up and returns their Authorization headers."""
    response = await http.post("/auth/register", json={"username": username, "email": email, "password": password})
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['tokens']['accessToken']}"}


async def sign_in(http: httpx.AsyncClient, email: str, password: str = PASSWORD) -> dict[str, str]:
    response = await http.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['tokens']['accessToken']}"}


@pytest.fixture
async def anonymous(mongo_available):
    """A fresh app (catalog loaded, no players) for each test, with no one signed in."""
    reset = AsyncMongoClient(MONGODB_URI)
    await reset.drop_database(TEST_DB)
    await reset.close()

    settings = Settings(
        mongodb_uri=MONGODB_URI,
        mongodb_db=TEST_DB,
        seed_on_startup=True,
        code_executor="local",
        jwt_secret="test-secret-" + "x" * 40,
        _env_file=None,
    )
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        app.state.providers = [StubProvider()]
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test/api/v1") as http:
            yield http


LEARNER = {"username": "Test Learner", "email": "learner@example.com"}


@pytest.fixture
async def client(anonymous):
    """The same app, signed in as a newly registered learner."""
    anonymous.headers.update(await register(anonymous, **LEARNER))
    return anonymous
