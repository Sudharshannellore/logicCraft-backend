import httpx

from app.core.config import Settings


def build_http_client(settings: Settings) -> httpx.AsyncClient:
    """One pooled client for all outbound calls, created and closed with the app."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(settings.http_timeout_seconds),
        headers={"User-Agent": settings.http_user_agent, "Accept": "application/json"},
        follow_redirects=True,
    )
