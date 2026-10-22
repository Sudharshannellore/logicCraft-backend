from app.core.config import Settings
from app.integrations.llm.openrouter import ChatMessage, LLMUnavailable, OpenRouterClient


def build_llm(http, settings: Settings) -> OpenRouterClient | None:
    """The language-model client, or None when no OpenRouter key is configured."""
    if not settings.openrouter_api_key:
        return None
    return OpenRouterClient(
        http,
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
        timeout_seconds=settings.openrouter_timeout_seconds,
        max_tokens=settings.openrouter_max_tokens,
        app_url=settings.openrouter_app_url,
        app_name=settings.openrouter_app_name,
    )


__all__ = ["ChatMessage", "LLMUnavailable", "OpenRouterClient", "build_llm"]
