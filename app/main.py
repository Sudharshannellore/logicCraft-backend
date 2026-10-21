import logging
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.routes import api_router
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.db.indexes import ensure_indexes
from app.db.mongo import Mongo
from app.integrations.execution import build_executor
from app.integrations.http import build_http_client
from app.integrations.tutorials import build_providers
from app.seed.seeder import seed_if_empty

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    if not settings.jwt_secret:
        if settings.environment == "production":
            raise RuntimeError("Set JWT_SECRET: tokens can't be signed safely without it.")
        logger.warning("JWT_SECRET is not set; using a random one, so every restart signs everyone out.")
        settings = settings.model_copy(update={"jwt_secret": secrets.token_urlsafe(64)})

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        mongo = Mongo(settings.mongodb_uri, settings.mongodb_db)
        http = build_http_client(settings)
        app.state.settings = settings
        app.state.mongo = mongo
        app.state.http = http
        app.state.providers = build_providers(http, settings)
        app.state.executor = build_executor(settings)
        try:
            await ensure_indexes(
                mongo.db,
                tutorial_cache_ttl_seconds=settings.tutorial_cache_ttl_seconds,
                login_lockout_seconds=settings.login_lockout_minutes * 60,
            )
            if settings.seed_on_startup and await seed_if_empty(mongo.db):
                logger.info("Loaded the course and practice catalog into an empty database.")
            yield
        finally:
            await http.aclose()
            await mongo.close()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Backend for Logicraft, a gamified coding-learning platform. Sign in with `POST /auth/login` and send "
            "`Authorization: Bearer <accessToken>`; in these docs, use **Authorize** with your email and password."
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
