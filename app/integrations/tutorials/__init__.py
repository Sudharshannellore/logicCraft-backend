from app.core.config import Settings
from app.integrations.tutorials.base import ImageProvider, ReferenceProvider, TutorialProvider
from app.integrations.tutorials.devto import DevToProvider
from app.integrations.tutorials.mdn import MdnProvider
from app.integrations.tutorials.stackexchange import StackExchangeProvider
from app.integrations.tutorials.wikipedia import WikipediaProvider
from app.integrations.tutorials.youtube import YouTubeProvider


def build_providers(http, settings: Settings) -> list[TutorialProvider]:
    """Every tutorial provider, enabled or not (disabled ones are listed but skipped)."""
    return [
        DevToProvider(http),
        StackExchangeProvider(http, api_key=settings.stackexchange_key),
        MdnProvider(http),
        WikipediaProvider(http),
        YouTubeProvider(http, api_key=settings.youtube_api_key),
    ]


__all__ = ["ImageProvider", "ReferenceProvider", "TutorialProvider", "build_providers"]
