import html
from datetime import UTC, datetime

from app.domain.languages import language as language_info
from app.integrations.tutorials.base import TutorialProvider
from app.schemas.tutorials import TutorialResource

API = "https://api.stackexchange.com/2.3/search/advanced"


class StackExchangeProvider(TutorialProvider):
    """Stack Overflow's most-voted answered questions on a topic. Free; a key only raises the daily quota."""

    name = "stackoverflow"
    label = "Stack Overflow"
    homepage = "https://stackoverflow.com"
    kinds = ["qa"]

    def __init__(self, http, api_key: str = ""):
        super().__init__(http)
        self.api_key = api_key

    async def _search(self, params: dict) -> list[dict]:
        response = await self.http.get(API, params=params)
        response.raise_for_status()
        return response.json().get("items", [])

    async def search(self, query: str, language: str | None, limit: int) -> list[TutorialResource]:
        params = {
            "order": "desc",
            "sort": "votes",
            "accepted": "True",
            "site": "stackoverflow",
            "pagesize": limit,
            "filter": "default",
        }
        if info := language_info(language):
            params["tagged"] = info.stackoverflow_tag
        if self.api_key:
            params["key"] = self.api_key
        # Questions *about* the topic (title match) beat ones that merely mention it.
        items = await self._search({**params, "title": query}) or await self._search({**params, "q": query})
        return [
            TutorialResource(
                id=f"stackoverflow:{q['question_id']}",
                provider=self.name,
                kind="qa",
                title=html.unescape(q["title"]),
                url=q["link"],
                summary=f"{q.get('answer_count', 0)} answers · {q.get('view_count', 0):,} views",
                author=html.unescape((q.get("owner") or {}).get("display_name", "")) or None,
                tags=q.get("tags", []),
                score=q.get("score", 0),
                published_at=datetime.fromtimestamp(q["creation_date"], UTC) if q.get("creation_date") else None,
            )
            for q in items
        ]
