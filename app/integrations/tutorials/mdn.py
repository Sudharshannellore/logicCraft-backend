from app.integrations.tutorials.base import ReferenceProvider, TutorialProvider
from app.schemas.tutorials import TutorialReference, TutorialResource

BASE = "https://developer.mozilla.org"
SEARCH = f"{BASE}/api/v1/search"


class MdnProvider(TutorialProvider, ReferenceProvider):
    """MDN Web Docs search — the reference for JavaScript and the web platform. Free, no key."""

    name = "mdn"
    label = "MDN Web Docs"
    homepage = BASE
    kinds = ["reference"]
    languages = {"javascript", "html", "css"}

    async def _search(self, query: str, limit: int) -> list[dict]:
        response = await self.http.get(SEARCH, params={"q": query, "locale": "en-US", "size": limit})
        response.raise_for_status()
        return response.json().get("documents", [])

    async def search(self, query: str, language: str | None, limit: int) -> list[TutorialResource]:
        return [
            TutorialResource(
                id=f"mdn:{d['slug']}",
                provider=self.name,
                kind="reference",
                title=d["title"],
                url=f"{BASE}{d['mdn_url']}",
                summary=d.get("summary") or None,
                score=round((d.get("popularity") or 0) * 1000),
            )
            for d in await self._search(query, limit)
        ]

    async def lookup(self, query: str, language: str | None) -> TutorialReference | None:
        if not self.supports(language):
            return None
        documents = await self._search(query, 1)
        if not documents:
            return None
        d = documents[0]
        return TutorialReference(
            provider=self.name, title=d["title"], summary=d.get("summary", ""), url=f"{BASE}{d['mdn_url']}"
        )
