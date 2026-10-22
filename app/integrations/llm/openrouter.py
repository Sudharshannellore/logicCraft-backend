"""OpenRouter chat completions (https://openrouter.ai/docs/api-reference/chat-completion).

One OpenAI-compatible endpoint that fronts many models; the model is chosen by `OPENROUTER_MODEL`.
Every failure becomes `LLMUnavailable`, so callers can fall back to something that always works.
"""

import logging
from typing import TypedDict

import httpx

logger = logging.getLogger(__name__)


class ChatMessage(TypedDict):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMUnavailable(Exception):
    """The model couldn't produce an answer (network, quota, bad response, empty reply)."""


class OpenRouterClient:
    def __init__(
        self,
        http: httpx.AsyncClient,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout_seconds: float = 30.0,
        max_tokens: int = 500,
        app_url: str = "",
        app_name: str = "Logicraft",
    ):
        self.http = http
        self.model = model
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.timeout = httpx.Timeout(timeout_seconds)
        self.max_tokens = max_tokens
        self._headers = {"Authorization": f"Bearer {api_key}", "X-Title": app_name}
        if app_url:
            self._headers["HTTP-Referer"] = app_url

    async def complete(self, messages: list[ChatMessage], *, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": temperature,
        }
        try:
            res = await self.http.post(self.url, json=payload, headers=self._headers, timeout=self.timeout)
        except httpx.HTTPError as exc:
            logger.warning("OpenRouter request failed: %s", type(exc).__name__)
            raise LLMUnavailable("The AI service couldn't be reached.") from exc
        if res.status_code != 200:
            logger.warning("OpenRouter returned HTTP %s: %s", res.status_code, res.text[:300])
            raise LLMUnavailable(f"The AI service answered with HTTP {res.status_code}.")
        try:
            data = res.json()
        except ValueError as exc:
            raise LLMUnavailable("The AI service sent an unreadable reply.") from exc
        # OpenRouter can report a provider failure inside a 200 response: {"error": {...}}.
        if data.get("error"):
            logger.warning("OpenRouter error: %s", str(data["error"])[:300])
            raise LLMUnavailable("The AI service reported an error.")
        try:
            text = (data["choices"][0]["message"]["content"] or "").strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMUnavailable("The AI service sent an unexpected reply.") from exc
        if not text:
            raise LLMUnavailable("The AI service sent an empty reply.")
        return text
