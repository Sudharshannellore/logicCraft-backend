"""Provider parsing and aggregation against recorded-shape responses — no network."""

import httpx
import pytest
import respx

from app.integrations.tutorials.base import is_relevant
from app.integrations.tutorials.devto import DevToProvider
from app.integrations.tutorials.mdn import MdnProvider
from app.integrations.tutorials.stackexchange import StackExchangeProvider
from app.integrations.tutorials.wikipedia import WikipediaProvider
from app.integrations.tutorials.youtube import YouTubeProvider
from app.services.tutorials import TutorialService


class MemoryCache:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def put(self, key, payload):
        self.data[key] = payload


@pytest.fixture
async def http():
    async with httpx.AsyncClient() as client:
        yield client


def test_relevance_needs_every_keyword_of_short_queries():
    assert is_relevant("binary search", "Binary search (bisection) in Python")
    assert is_relevant("binary search", "Coco eating banana", None, "java binarysearch")
    assert not is_relevant("binary search", "What is AI Search?")
    assert is_relevant("closures", "Understanding JavaScript Closure")
    assert not is_relevant("go", "Algorithms 101")


@respx.mock
async def test_devto_keeps_only_on_topic_articles(http):
    article = {
        "id": 1,
        "title": "Recursion explained",
        "description": "Base cases and call stacks",
        "url": "https://dev.to/a/recursion",
        "tag_list": ["python", "recursion"],
        "positive_reactions_count": 12,
        "reading_time_minutes": 4,
        "user": {"name": "Ada"},
    }
    off_topic = {**article, "id": 2, "title": "My week", "description": "", "tag_list": ["python"]}
    respx.get("https://dev.to/api/articles").mock(return_value=httpx.Response(200, json=[article, off_topic]))
    results = await DevToProvider(http).search("Recursion", "python", 5)
    assert [r.title for r in results] == ["Recursion explained"]
    assert results[0].author == "Ada" and results[0].reading_minutes == 4


@respx.mock
async def test_stackexchange_falls_back_from_title_to_full_text(http):
    route = respx.get("https://api.stackexchange.com/2.3/search/advanced")
    route.side_effect = [
        httpx.Response(200, json={"items": []}),
        httpx.Response(
            200,
            json={
                "items": [
                    {
                        "question_id": 7,
                        "title": "What&#39;s a closure?",
                        "link": "https://so/q/7",
                        "score": 99,
                        "tags": ["javascript"],
                    }
                ]
            },
        ),
    ]
    results = await StackExchangeProvider(http).search("closure", "javascript", 3)
    assert results[0].title == "What's a closure?"
    assert "title" in str(route.calls[0].request.url) and "q=closure" in str(route.calls[1].request.url)


@respx.mock
async def test_wikipedia_reference_skips_disambiguation_pages(http):
    respx.get("https://en.wikipedia.org/w/rest.php/v1/search/page").mock(
        return_value=httpx.Response(200, json={"pages": [{"key": "Loop"}, {"key": "For_loop"}]})
    )
    respx.get("https://en.wikipedia.org/api/rest_v1/page/summary/Loop").mock(
        return_value=httpx.Response(200, json={"type": "disambiguation", "extract": "Loop may refer to"})
    )
    respx.get("https://en.wikipedia.org/api/rest_v1/page/summary/For_loop").mock(
        return_value=httpx.Response(
            200,
            json={
                "title": "For loop",
                "extract": "A for loop repeats.",
                "content_urls": {"desktop": {"page": "https://w/For_loop"}},
            },
        )
    )
    reference = await WikipediaProvider(http).lookup("loops", "python")
    assert reference.title == "For loop"


async def test_language_specific_providers_stay_in_their_lane(http):
    assert MdnProvider(http).supports("javascript")
    assert not MdnProvider(http).supports("python") and not MdnProvider(http).supports(None)
    assert WikipediaProvider(http).supports(None)
    assert not YouTubeProvider(http).enabled and YouTubeProvider(http, api_key="k").enabled


@respx.mock
async def test_search_survives_a_failing_provider_and_caches(http):
    respx.get("https://dev.to/api/articles").mock(return_value=httpx.Response(503))
    respx.get("https://api.stackexchange.com/2.3/search/advanced").mock(
        return_value=httpx.Response(
            200, json={"items": [{"question_id": 1, "title": "Python loops", "link": "https://so/q/1", "tags": []}]}
        )
    )
    cache = MemoryCache()
    service = TutorialService([DevToProvider(http), StackExchangeProvider(http)], cache, timeout_seconds=2)

    first = await service.search("loops", language="python")
    statuses = {p.name: p for p in first.providers}
    assert not statuses["devto"].ok and statuses["stackoverflow"].ok
    assert [r.title for r in first.resources] == ["Python loops"]

    second = await service.search("loops", language="python")
    assert {p.name: p.cached for p in second.providers}["stackoverflow"]


@respx.mock
async def test_providers_use_each_platforms_name_for_the_language(http):
    so = respx.get("https://api.stackexchange.com/2.3/search/advanced").mock(
        return_value=httpx.Response(200, json={"items": []})
    )
    await StackExchangeProvider(http).search("LINQ", "csharp", 3)
    assert so.calls[0].request.url.params["tagged"] == "c#"

    dev = respx.get("https://dev.to/api/articles").mock(return_value=httpx.Response(200, json=[]))
    await DevToProvider(http).search("templates", "cpp", 3)
    assert "cpp" in {call.request.url.params["tag"] for call in dev.calls}


def test_language_matching_keeps_courses_on_their_own_language():
    from app.domain.languages import mentions_language, names_other_language

    assert names_other_language("csharp", "C data types")  # C, not C#
    assert not names_other_language("cpp", "C data types")  # close sibling
    assert not names_other_language("typescript", "JavaScript closures")
    assert names_other_language("javascript", "Java (programming language)")
    assert mentions_language("go", "Go channels explained") and not mentions_language("go", "ready, set, go")


@respx.mock
async def test_devto_drops_articles_about_other_languages(http):
    article = {
        "title": "Variables in JavaScript",
        "description": "",
        "url": "u",
        "tag_list": ["javascript", "variables"],
    }
    csharp = {**article, "id": 2, "title": "Variables in C#", "tag_list": ["csharp", "variables"]}
    respx.get("https://dev.to/api/articles").mock(return_value=httpx.Response(200, json=[{**article, "id": 1}, csharp]))
    results = await DevToProvider(http).search("variables", "csharp", 5)
    assert [r.title for r in results] == ["Variables in C#"]
