import asyncio
import logging
from collections.abc import Awaitable, Callable

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


def keep_alive_target(settings: Settings) -> str | None:
    """Public health URL to ping, or None when keep-alive is off (e.g. local development)."""
    base = settings.keep_alive_url or settings.render_external_url
    if not base:
        return None
    return f"{base.rstrip('/')}{settings.api_prefix}/health"


async def keep_alive_loop(
    url: str | None, interval_seconds: int, db_touch: Callable[[], Awaitable[None]] | None = None
) -> None:
    """Every interval: ping our own public URL (Render's free tier idles after ~15 min) and read from the
    database (Atlas M0 pauses clusters after 60 days without activity)."""
    async with httpx.AsyncClient(timeout=20) as client:
        while True:
            await asyncio.sleep(interval_seconds)
            if url:
                try:
                    response = await client.get(url)
                    logger.info("keep-alive ping -> %s", response.status_code)
                except Exception as exc:  # never let a failed ping stop the loop
                    logger.warning("keep-alive ping failed: %s", exc)
            if db_touch:
                try:
                    await db_touch()
                except Exception as exc:
                    logger.warning("keep-alive db read failed: %s", exc)
