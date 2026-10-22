"""OpenRouter client and Quest AI's use of it: success, every failure mode, and the rule-based fallback."""

import json

import httpx
import pytest

from app.domain import mentor
from app.integrations.llm import LLMUnavailable, OpenRouterClient
from app.services.mentor import MentorService

PROBLEM = mentor.ProblemContext(
    title="Two Sum",
    description="Return the indices of two numbers that add up to target.",
    tags=["Array", "Hash Table"],
    hints=["Try brute force first.", "A hash map finds complements in O(1)."],
    examples=[{"input": "nums = [2,7], target = 9", "output": "[0,1]"}],
)


def client_for(handler) -> OpenRouterClient:
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return OpenRouterClient(http, api_key="sk-test", model="test/model", app_url="https://logicraft.test")


def reply(content, status=200):
    return httpx.Response(status, json={"choices": [{"message": {"role": "assistant", "content": content}}]})


async def test_complete_sends_model_key_and_messages():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["referer"] = request.headers["http-referer"]
        seen["body"] = json.loads(request.content)
        return reply("  Use a hash map.  ")

    text = await client_for(handler).complete([{"role": "user", "content": "hi"}])
    assert text == "Use a hash map."
    assert seen["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert seen["auth"] == "Bearer sk-test"
    assert seen["referer"] == "https://logicraft.test"
    assert seen["body"]["model"] == "test/model"
    assert seen["body"]["messages"] == [{"role": "user", "content": "hi"}]


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(429, json={"error": {"message": "rate limited"}}),
        httpx.Response(502, text="bad gateway"),
        httpx.Response(200, text="not json"),
        httpx.Response(200, json={"error": {"message": "provider down"}}),
        httpx.Response(200, json={"choices": []}),
        httpx.Response(200, json={"choices": [{"message": {"content": "  "}}]}),
    ],
)
async def test_bad_responses_are_unavailable(response):
    with pytest.raises(LLMUnavailable):
        await client_for(lambda request: response).complete([{"role": "user", "content": "hi"}])


async def test_network_errors_are_unavailable():
    def handler(request):
        raise httpx.ConnectTimeout("slow")

    with pytest.raises(LLMUnavailable):
        await client_for(handler).complete([{"role": "user", "content": "hi"}])


def test_prompt_carries_the_problem_and_this_turns_hint_only():
    messages = mentor.build_messages("hint please", PROBLEM, turn=1)
    system = messages[0]["content"]
    assert messages[0]["role"] == "system" and messages[1] == {"role": "user", "content": "hint please"}
    assert "Two Sum" in system and "nums = [2,7]" in system
    assert "A hash map finds complements" in system and "Try brute force first" not in system


class FakeLLM:
    def __init__(self, result):
        self.result = result

    async def complete(self, messages):
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def service(llm) -> MentorService:
    return MentorService(None, None, None, llm)


async def test_service_prefers_the_model():
    assert await service(FakeLLM("From the model."))._reply("hint", PROBLEM, 0) == "From the model."


async def test_service_falls_back_when_the_model_fails():
    text = await service(FakeLLM(LLMUnavailable("down")))._reply("hint please", PROBLEM, 0)
    assert text == "Hint: Try brute force first."


async def test_service_without_a_key_uses_the_rule_based_mentor():
    assert await service(None)._reply("hint please", PROBLEM, 1) == "Hint: A hash map finds complements in O(1)."
