"""Exercism (exercism.org) as a live source of practice exercises.

Every Exercism track is an MIT-licensed GitHub repository: `config.json` lists its exercises, and each
exercise folder holds its instructions, a starter file and the test suite. We read them straight
from raw.githubusercontent.com (no API key, no rate-limited API) and cache them in MongoDB, so new
exercises appear on their own and each file is fetched about once a week.
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

import httpx

from app.repositories.exercism_cache import ExercismCacheRepository

logger = logging.getLogger(__name__)

RAW = "https://raw.githubusercontent.com/exercism/{track}/main/{path}"
WEBSITE = "https://exercism.org/tracks/{track}/exercises/{slug}"
TRACK_TTL = 24 * 60 * 60
EXERCISE_TTL = 7 * 24 * 60 * 60
MAX_FILE_BYTES = 256_000
# Status values Exercism uses for exercises that aren't ready for learners.
_HIDDEN = {"deprecated", "wip"}
# Files the SQLite shell scripts pull in with .read / .import.
_SQL_REFERENCE = re.compile(r"^\s*\.(?:read|import)\s+(?:--\S+\s+)*['\"]?(?:\./)?([\w.\-/]+)['\"]?", re.M)


class ExercismUnavailable(Exception):
    """GitHub couldn't be reached and nothing usable is cached."""


@dataclass(frozen=True)
class ExerciseSummary:
    slug: str
    name: str
    difficulty: int
    topics: list[str]


@dataclass(frozen=True)
class ExerciseFiles:
    slug: str
    name: str
    blurb: str
    instructions: str
    # name -> content. `solution` is what the learner edits; `tests` and `support` stay as published.
    solution: dict[str, str]
    tests: dict[str, str]
    support: dict[str, str]
    source: str | None
    source_url: str | None


def website_url(track: str, slug: str) -> str:
    return WEBSITE.format(track=track, slug=slug)


class ExercismClient:
    def __init__(self, http: httpx.AsyncClient, cache: ExercismCacheRepository):
        self.http = http
        self.cache = cache

    async def _raw(self, track: str, path: str) -> str | None:
        """A file from the track repo, or None if it doesn't exist."""
        try:
            response = await self.http.get(RAW.format(track=track, path=path))
        except httpx.HTTPError as exc:
            raise ExercismUnavailable(f"Couldn't reach GitHub: {type(exc).__name__}") from exc
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise ExercismUnavailable(f"GitHub returned {response.status_code} for {path}")
        if len(response.content) > MAX_FILE_BYTES:
            return None
        return response.text

    async def exercises(self, track: str) -> list[ExerciseSummary]:
        key = f"track:{track}"
        cached = await self.cache.get(key)
        if cached is None:
            text = await self._raw(track, "config.json")
            if text is None:
                raise ExercismUnavailable(f"Exercism has no {track} track.")
            config = json.loads(text)
            cached = [
                {
                    "slug": e["slug"],
                    "name": e.get("name") or e["slug"].replace("-", " ").title(),
                    "difficulty": int(e.get("difficulty") or 1),
                    "topics": sorted(set(e.get("practices") or []) | set(e.get("topics") or [])),
                }
                for e in config.get("exercises", {}).get("practice", [])
                if e.get("status", "active") not in _HIDDEN
            ]
            await self.cache.put(key, cached, ttl_seconds=TRACK_TTL)
        return [ExerciseSummary(**e) for e in cached]

    async def exercise(self, track: str, slug: str) -> ExerciseFiles | None:
        key = f"exercise:{track}:{slug}"
        cached = await self.cache.get(key)
        if cached is None:
            cached = await self._fetch_exercise(track, slug)
            if cached is None:
                return None
            await self.cache.put(key, cached, ttl_seconds=EXERCISE_TTL)
        return ExerciseFiles(**cached)

    async def _fetch_exercise(self, track: str, slug: str) -> dict[str, Any] | None:
        base = f"exercises/practice/{slug}"
        meta_text = await self._raw(track, f"{base}/.meta/config.json")
        if meta_text is None:
            return None
        meta = json.loads(meta_text)
        files = meta.get("files", {})

        async def fetch_many(paths: list[str]) -> dict[str, str]:
            texts = await asyncio.gather(*(self._raw(track, f"{base}/{p}") for p in paths))
            return {p: t for p, t in zip(paths, texts, strict=True) if t is not None}

        solution_paths, test_paths = files.get("solution", []), files.get("test", [])
        support_paths = [*files.get("editor", []), *files.get("additional", [])]
        docs_paths = [".docs/introduction.md", ".docs/instructions.md", ".docs/instructions.append.md"]
        solution, tests, support, docs = await asyncio.gather(
            fetch_many(solution_paths), fetch_many(test_paths), fetch_many(support_paths), fetch_many(docs_paths)
        )
        if not solution or not tests:
            return None
        if track == "sqlite":
            support |= await self._sql_dependencies(track, base, {**solution, **tests, **support})

        name = next((e.name for e in await self.exercises(track) if e.slug == slug), slug.replace("-", " ").title())
        instructions = "\n\n".join(docs[p].strip() for p in docs_paths if p in docs)
        flat = lambda d: {PurePosixPath(k).name: v for k, v in d.items()}  # noqa: E731
        return {
            "slug": slug,
            "name": name,
            "blurb": meta.get("blurb", ""),
            "instructions": instructions,
            "solution": flat(solution),
            "tests": flat(tests),
            "support": flat(support),
            "source": meta.get("source"),
            "source_url": meta.get("source_url"),
        }

    async def _sql_dependencies(self, track: str, base: str, known: dict[str, str]) -> dict[str, str]:
        """Follows `.read` / `.import` references so every script and CSV fixture is available."""
        found: dict[str, str] = {}
        pending = [t for t in known.values()]
        seen = set(known)
        while pending:
            script = pending.pop()
            for name in _SQL_REFERENCE.findall(script):
                if name in seen or name.endswith((".json", ".md")):  # outputs, not inputs
                    continue
                seen.add(name)
                text = await self._raw(track, f"{base}/{name}")
                if text is not None:
                    found[name] = text
                    if name.endswith(".sql"):
                        pending.append(text)
        return found
