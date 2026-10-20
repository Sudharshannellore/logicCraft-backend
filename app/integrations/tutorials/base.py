import re
from abc import ABC, abstractmethod

import httpx

from app.schemas.tutorials import ResourceKind, TutorialReference, TutorialResource

_WORD = re.compile(r"[a-z0-9+#]+")
_STOPWORDS = {"a", "an", "and", "the", "of", "in", "to", "with", "for", "on", "how", "what", "is", "basics"}


def keywords(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS and len(w) > 1}


def _stem(word: str) -> str:
    """Crude plural folding so "closures" finds "closure" and "dictionaries" finds "dictionary"."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def relevance(query: str, *texts: str | None) -> int:
    """How many of the query's keywords appear in the texts.

    Longer keywords match anywhere (so "search" is found in the tag "binarysearch"); short ones must
    start a word (so "go" doesn't match "algorithm").
    """
    haystack = " ".join(t for t in texts if t).lower()
    words = _WORD.findall(haystack)
    hits = 0
    for word in (_stem(w) for w in keywords(query)):
        if len(word) >= 4 and word in haystack or any(w.startswith(word) for w in words):
            hits += 1
    return hits


def is_relevant(query: str, *texts: str | None) -> bool:
    """Every keyword for short queries; at least 60% of them for longer ones."""
    wanted = len(keywords(query))
    if wanted == 0:
        return True
    needed = wanted if wanted <= 2 else -(-wanted * 3 // 5)
    return relevance(query, *texts) >= needed


class TutorialProvider(ABC):
    """A free external platform that returns tutorials for a topic."""

    name: str
    label: str
    homepage: str
    kinds: list[ResourceKind]
    requires_key: bool = False
    # Languages the platform covers well; None = all.
    languages: set[str] | None = None

    def __init__(self, http: httpx.AsyncClient):
        self.http = http

    @property
    def enabled(self) -> bool:
        return True

    def supports(self, language: str | None) -> bool:
        """Language-specific platforms (e.g. MDN) only join searches in their own languages."""
        return self.languages is None or language in self.languages

    @abstractmethod
    async def search(self, query: str, language: str | None, limit: int) -> list[TutorialResource]: ...


class ReferenceProvider(ABC):
    """A platform that can explain a single concept (encyclopedia / docs summary)."""

    @abstractmethod
    async def lookup(self, query: str, language: str | None) -> TutorialReference | None: ...
