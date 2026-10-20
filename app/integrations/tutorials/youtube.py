import html

from app.domain.languages import language as language_info
from app.integrations.tutorials.base import TutorialProvider
from app.schemas.tutorials import TutorialResource

API = "https://www.googleapis.com/youtube/v3/search"


class YouTubeProvider(TutorialProvider):
    """YouTube Data API v3 video tutorials. The API is free but needs a key — disabled without one."""

    name = "youtube"
    label = "YouTube"
    homepage = "https://www.youtube.com"
    kinds = ["video"]
    requires_key = True

    def __init__(self, http, api_key: str = ""):
        super().__init__(http)
        self.api_key = api_key

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def search(self, query: str, language: str | None, limit: int) -> list[TutorialResource]:
        info = language_info(language)
        q = f"{query} {info.name if info else ''} tutorial for beginners".replace("  ", " ")
        response = await self.http.get(
            API,
            params={
                "part": "snippet",
                "type": "video",
                "q": q,
                "maxResults": limit,
                "relevanceLanguage": "en",
                "videoEmbeddable": "true",
                "safeSearch": "strict",
                "key": self.api_key,
            },
        )
        response.raise_for_status()
        return [
            TutorialResource(
                id=f"youtube:{item['id']['videoId']}",
                provider=self.name,
                kind="video",
                title=html.unescape(item["snippet"]["title"]),
                url=f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                summary=html.unescape(item["snippet"].get("description", "")) or None,
                author=item["snippet"].get("channelTitle"),
                thumbnail_url=((item["snippet"].get("thumbnails") or {}).get("medium") or {}).get("url"),
                published_at=item["snippet"].get("publishedAt"),
            )
            for item in response.json().get("items", [])
            if item.get("id", {}).get("videoId")
        ]
