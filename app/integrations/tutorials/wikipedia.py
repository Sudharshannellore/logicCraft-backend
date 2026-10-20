from urllib.parse import quote

from app.domain.languages import language as language_info
from app.domain.languages import names_other_language
from app.integrations.tutorials.base import ReferenceProvider, TutorialProvider
from app.schemas.tutorials import TutorialReference, TutorialResource

SEARCH = "https://en.wikipedia.org/w/rest.php/v1/search/page"
SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{key}"


class WikipediaProvider(TutorialProvider, ReferenceProvider):
    """Wikipedia's REST API: computer-science background for a concept. Free, no key (User-Agent required)."""

    name = "wikipedia"
    label = "Wikipedia"
    homepage = "https://en.wikipedia.org"
    kinds = ["reference"]

    async def _search(self, query: str, language: str | None, limit: int) -> list[dict]:
        info = language_info(language)
        context = info.wikipedia_context if info else "programming"
        # Ask for a few extra: pages about a different language (e.g. "C data types" for C#) are dropped.
        response = await self.http.get(SEARCH, params={"q": f"{query} {context}", "limit": limit + 3})
        response.raise_for_status()
        pages = response.json().get("pages", [])
        if info:
            pages = [
                p
                for p in pages
                if not names_other_language(info.id, f"{p.get('title', p['key'])} {p.get('description') or ''}")
            ]
        return pages[:limit]

    async def _summary(self, key: str) -> dict | None:
        response = await self.http.get(SUMMARY.format(key=quote(key, safe="")))
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return None if data.get("type") == "disambiguation" else data

    async def lookup(self, query: str, language: str | None) -> TutorialReference | None:
        for page in await self._search(query, language, 3):
            data = await self._summary(page["key"])
            if data and data.get("extract"):
                return TutorialReference(
                    provider=self.name,
                    title=data["title"],
                    summary=data["extract"],
                    url=data["content_urls"]["desktop"]["page"],
                    thumbnail_url=(data.get("thumbnail") or {}).get("source"),
                )
        return None

    async def search(self, query: str, language: str | None, limit: int) -> list[TutorialResource]:
        return [
            TutorialResource(
                id=f"wikipedia:{p['key']}",
                provider=self.name,
                kind="reference",
                title=p["title"],
                url=f"https://en.wikipedia.org/wiki/{quote(p['key'])}",
                summary=p.get("description") or None,
                thumbnail_url=("https:" + p["thumbnail"]["url"]) if (p.get("thumbnail") or {}).get("url") else None,
            )
            for p in await self._search(query, language, limit)
        ]
