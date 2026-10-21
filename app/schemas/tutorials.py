from datetime import datetime
from typing import Literal

from app.schemas.common import CamelModel

ResourceKind = Literal["article", "video", "qa", "reference"]


class TutorialResource(CamelModel):
    """One external tutorial, normalised across providers."""

    id: str
    provider: str
    kind: ResourceKind
    title: str
    url: str
    summary: str | None = None
    author: str | None = None
    thumbnail_url: str | None = None
    tags: list[str] = []
    # Provider-native popularity signal (reactions, votes, views) — used for ranking.
    score: int = 0
    reading_minutes: int | None = None
    published_at: datetime | None = None


class TutorialReference(CamelModel):
    """A short encyclopedic/reference explanation of a concept (Wikipedia, MDN)."""

    provider: str
    title: str
    summary: str
    url: str
    thumbnail_url: str | None = None


class TutorialImage(CamelModel):
    """A diagram or picture that illustrates a concept, with where it came from (credit and licence live there)."""

    url: str
    caption: str | None = None
    source_url: str
    provider: str


class ProviderStatus(CamelModel):
    name: str
    ok: bool
    count: int = 0
    cached: bool = False
    error: str | None = None


class TutorialSearchResult(CamelModel):
    query: str
    language: str | None
    resources: list[TutorialResource]
    providers: list[ProviderStatus]


class ProviderInfo(CamelModel):
    name: str
    label: str
    kinds: list[ResourceKind]
    enabled: bool
    requires_key: bool
    homepage: str
