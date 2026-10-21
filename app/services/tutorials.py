"""Aggregates free external tutorial platforms into one ranked, cached list.

Providers run concurrently with their own timeouts. A provider that fails or times out is
reported in `providers` and skipped — it never fails the whole request.
"""

import asyncio
import logging

from pydantic import TypeAdapter

from app.core.errors import UnprocessableError
from app.integrations.tutorials import ImageProvider, ReferenceProvider, TutorialProvider
from app.integrations.tutorials.base import is_relevant
from app.repositories.tutorial_cache import TutorialCacheRepository
from app.schemas.tutorials import (
    ProviderInfo,
    ProviderStatus,
    TutorialImage,
    TutorialReference,
    TutorialResource,
    TutorialSearchResult,
)

logger = logging.getLogger(__name__)

_resources = TypeAdapter(list[TutorialResource])
_images = TypeAdapter(list[TutorialImage])
# Interleave kinds so one chatty provider can't crowd out the rest.
_KIND_ORDER = {"reference": 0, "article": 1, "video": 2, "qa": 3}


class TutorialService:
    def __init__(self, providers: list[TutorialProvider], cache: TutorialCacheRepository, *, timeout_seconds: float):
        self.providers = providers
        self.cache = cache
        self.timeout_seconds = timeout_seconds

    def provider_info(self) -> list[ProviderInfo]:
        return [
            ProviderInfo(
                name=p.name,
                label=p.label,
                kinds=p.kinds,
                enabled=p.enabled,
                requires_key=p.requires_key,
                homepage=p.homepage,
            )
            for p in self.providers
        ]

    async def _from_provider(
        self, provider: TutorialProvider, query: str, language: str | None, limit: int
    ) -> tuple[ProviderStatus, list[TutorialResource]]:
        key = f"search:{provider.name}:{language or '-'}:{limit}:{query.lower()}"
        cached = await self.cache.get(key)
        if cached is not None:
            items = _resources.validate_python(cached)
            return ProviderStatus(name=provider.name, ok=True, count=len(items), cached=True), items
        try:
            items = await asyncio.wait_for(provider.search(query, language, limit), self.timeout_seconds)
        except Exception as exc:  # network errors, bad payloads, timeouts — degrade, don't fail
            logger.warning("Tutorial provider %s failed for %r: %r", provider.name, query, exc)
            return ProviderStatus(name=provider.name, ok=False, error=type(exc).__name__), []
        # Every platform's search is fuzzy; keep only results that are actually about the topic.
        items = [r for r in items if is_relevant(query, r.title, r.summary, " ".join(r.tags))]
        await self.cache.put(key, _resources.dump_python(items, mode="json"))
        return ProviderStatus(name=provider.name, ok=True, count=len(items)), items

    async def search(
        self, query: str, *, language: str | None = None, providers: list[str] | None = None, limit: int = 5
    ) -> TutorialSearchResult:
        query = " ".join(query.split())
        if len(query) < 2:
            raise UnprocessableError("Search for at least 2 characters.")
        if providers:
            unknown = set(providers) - {p.name for p in self.providers}
            if unknown:
                raise UnprocessableError(f"Unknown provider(s): {', '.join(sorted(unknown))}.")
        selected = [
            p for p in self.providers if p.enabled and p.supports(language) and (not providers or p.name in providers)
        ]
        outcomes = await asyncio.gather(*(self._from_provider(p, query, language, limit) for p in selected))

        # Round-robin across providers (best of each first), then by kind.
        lists = [items for _, items in outcomes]
        merged: list[TutorialResource] = []
        for i in range(max((len(x) for x in lists), default=0)):
            merged.extend(sorted((x[i] for x in lists if i < len(x)), key=lambda r: _KIND_ORDER.get(r.kind, 9)))
        return TutorialSearchResult(
            query=query, language=language, resources=merged, providers=[s for s, _ in outcomes]
        )

    async def reference(self, query: str, language: str | None = None) -> TutorialReference | None:
        """Short explanation of a concept: MDN for web languages, otherwise Wikipedia."""
        key = f"reference:{language or '-'}:{query.lower()}"
        cached = await self.cache.get(key)
        if cached is not None:
            return TutorialReference.model_validate(cached) if cached else None
        references = [
            p for p in self.providers if isinstance(p, ReferenceProvider) and p.enabled and p.supports(language)
        ]
        # Language-specific references (MDN) before general ones (Wikipedia).
        references.sort(key=lambda p: p.languages is None)
        for provider in references:
            try:
                found = await asyncio.wait_for(provider.lookup(query, language), self.timeout_seconds)
            except Exception as exc:
                logger.warning("Reference provider %s failed for %r: %r", provider.name, query, exc)
                continue
            if found:
                await self.cache.put(key, found.model_dump(mode="json"))
                return found
        return None

    async def images(self, query: str, language: str | None = None, limit: int = 4) -> list[TutorialImage]:
        """Pictures that illustrate a concept. Always best-effort: any failure just means no pictures."""
        key = f"images:{language or '-'}:{limit}:{query.lower()}"
        cached = await self.cache.get(key)
        if cached is not None:
            return _images.validate_python(cached)
        for provider in (p for p in self.providers if isinstance(p, ImageProvider) and p.enabled):
            try:
                found = await asyncio.wait_for(provider.images(query, language, limit), self.timeout_seconds)
            except Exception as exc:
                logger.warning("Image provider %s failed for %r: %r", provider.name, query, exc)
                continue
            await self.cache.put(key, _images.dump_python(found, mode="json"))
            if found:
                return found
        return []
