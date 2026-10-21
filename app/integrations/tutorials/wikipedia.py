import re
from urllib.parse import quote

from app.domain.languages import language as language_info
from app.domain.languages import names_other_language
from app.integrations.tutorials.base import ImageProvider, ReferenceProvider, TutorialProvider, is_relevant, keywords
from app.schemas.tutorials import TutorialImage, TutorialReference, TutorialResource

SEARCH = "https://en.wikipedia.org/w/rest.php/v1/search/page"
SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{key}"
MEDIA = "https://en.wikipedia.org/api/rest_v1/page/media-list/{key}"
# Site furniture that appears on many pages: logos, status icons, flags, audio.
_NOT_AN_ILLUSTRATION = re.compile(
    r"logo|icon|symbol|flag|commons|wiki|question[_ ]book|ambox|edit-|padlock|disambig|portal|nuvola|"
    r"increase|decrease|\.(ogg|oga|mp3|webm|ogv)$",
    re.I,
)


class WikipediaProvider(TutorialProvider, ReferenceProvider, ImageProvider):
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

    async def images(self, query: str, language: str | None, limit: int) -> list[TutorialImage]:
        """Diagrams from the best-matching article (e.g. "Linked list" → its node diagrams)."""
        if not keywords(query):  # "Basics" alone would match any article
            return []
        for page in await self._search(query, language, 3):
            if not is_relevant(query, page.get("title"), page.get("description")):
                continue
            response = await self.http.get(MEDIA.format(key=quote(page["key"], safe="")))
            if response.status_code == 404:
                continue
            response.raise_for_status()
            found = []
            for item in response.json().get("items", []):
                srcset = item.get("srcset") or []
                if item.get("type") != "image" or not item.get("showInGallery") or not srcset:
                    continue
                if _NOT_AN_ILLUSTRATION.search(item.get("title", "")):
                    continue
                src = srcset[-1]["src"]  # the largest rendition on offer
                found.append(
                    TutorialImage(
                        url="https:" + src if src.startswith("//") else src,
                        caption=((item.get("caption") or {}).get("text") or "").strip() or None,
                        source_url="https://en.wikipedia.org/wiki/" + quote(item["title"], safe=":"),
                        provider=self.name,
                    )
                )
            if found:
                return found[:limit]
        return []

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
