import asyncio
import re

from app.domain.languages import language as language_info
from app.domain.languages import mentions_language
from app.integrations.tutorials.base import TutorialProvider, is_relevant, keywords, relevance
from app.schemas.tutorials import TutorialResource

API = "https://dev.to/api/articles"


class DevToProvider(TutorialProvider):
    """DEV Community (Forem) public API — no key needed. Articles are found by tag, then ranked by topic match."""

    name = "devto"
    label = "DEV Community"
    homepage = "https://dev.to"
    kinds = ["article"]

    async def _by_tag(self, tag: str) -> list[dict]:
        response = await self.http.get(API, params={"tag": tag, "per_page": 30, "top": 365})
        response.raise_for_status()
        return response.json()

    async def search(self, query: str, language: str | None, limit: int) -> list[TutorialResource]:
        # DEV tags are single lowercase words; try the topic's own words as tags plus the language.
        tags = [re.sub(r"[^a-z0-9]", "", w) for w in sorted(keywords(query), key=len, reverse=True)[:2]]
        if info := language_info(language):
            tags.append(info.devto_tag)
        tags = list(dict.fromkeys(t for t in tags if t))
        batches = await asyncio.gather(*(self._by_tag(t) for t in tags), return_exceptions=True)

        seen: dict[int, dict] = {}
        for batch in batches:
            if isinstance(batch, BaseException):
                continue
            for article in batch:
                seen.setdefault(article["id"], article)
        if not seen and batches and isinstance(batches[0], BaseException):
            raise batches[0]

        def about_language(a: dict) -> bool:
            # Topic tags like "variables" return articles in every language; keep this course's.
            text = f"{a.get('title', '')} {a.get('description', '')}"
            return info is None or info.devto_tag in (a.get("tag_list") or []) or mentions_language(info.id, text)

        ranked = sorted(
            (
                (relevance(query, a.get("title"), a.get("description"), " ".join(a.get("tag_list") or [])), a)
                for a in seen.values()
                if about_language(a)
            ),
            key=lambda pair: (pair[0], pair[1].get("positive_reactions_count", 0)),
            reverse=True,
        )
        return [
            TutorialResource(
                id=f"devto:{a['id']}",
                provider=self.name,
                kind="article",
                title=a["title"],
                url=a["url"],
                summary=a.get("description") or None,
                author=(a.get("user") or {}).get("name"),
                thumbnail_url=a.get("cover_image") or a.get("social_image"),
                tags=list(a.get("tag_list") or []),
                score=a.get("positive_reactions_count", 0),
                reading_minutes=a.get("reading_time_minutes"),
                published_at=a.get("published_at"),
            )
            for _, a in ranked
            if is_relevant(query, a.get("title"), a.get("description"), " ".join(a.get("tag_list") or []))
        ][:limit]
