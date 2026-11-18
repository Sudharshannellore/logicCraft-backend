import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.routes import api_router
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.core.keep_alive import keep_alive_loop, keep_alive_target
from app.core.logging import configure_logging
from app.db.indexes import ensure_indexes
from app.db.mongo import Mongo
from app.integrations.execution import build_executor
from app.integrations.http import build_http_client
from app.integrations.tutorials import build_providers
from app.seed.seeder import seed_if_empty
from app.services.demo import ensure_demo_user

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        mongo = Mongo(settings.mongodb_uri, settings.mongodb_db)
        http = build_http_client(settings)
        app.state.settings = settings
        app.state.mongo = mongo
        app.state.http = http
        app.state.providers = build_providers(http, settings)
        app.state.executor = build_executor(settings)
        keep_alive_task: asyncio.Task | None = None
        try:
            await ensure_indexes(mongo.db, tutorial_cache_ttl_seconds=settings.tutorial_cache_ttl_seconds)
            await ensure_demo_user(mongo.db, with_data=settings.demo_data)
            if settings.seed_on_startup and await seed_if_empty(mongo.db):
                logger.info("Loaded the course and practice catalog into an empty database.")
            keep_alive_url = keep_alive_target(settings)
            if keep_alive_url:
                async def touch_db() -> None:
                    # A real read, so Atlas counts it as activity (it pauses idle free clusters after 60 days).
                    await mongo.db.command("ping")
                    names = await mongo.db.list_collection_names()
                    if names:
                        await mongo.db[names[0]].find_one({}, {"_id": 1})

                keep_alive_task = asyncio.create_task(
                    keep_alive_loop(keep_alive_url, settings.keep_alive_interval_seconds, touch_db)
                )
                logger.info("Keep-alive pinging %s every %ss.", keep_alive_url, settings.keep_alive_interval_seconds)
            yield
        finally:
            if keep_alive_task:
                keep_alive_task.cancel()
            await http.aclose()
            await mongo.close()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Backend for Logicraft, a gamified coding-learning platform. This is a showcase: there is no sign-in, "
            "every request acts as the shared demo player."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)  # lesson and course JSON compresses ~10x
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
