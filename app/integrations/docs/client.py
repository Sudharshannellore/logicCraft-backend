"""Open-source documentation repositories on GitHub, as a live source for framework courses.

A directory listing comes from GitHub's git-tree API (one request per directory, optionally authenticated
with GITHUB_TOKEN) and file contents from raw.githubusercontent.com. Both are cached in MongoDB, so a
repository is listed about once a day and a page is fetched about once a week.
"""

import logging
from dataclasses import dataclass

import httpx

from app.repositories.exercism_cache import ExercismCacheRepository

logger = logging.getLogger(__name__)

API = "https://api.github.com/repos/{repo}/git/trees/{ref}"
RAW = "https://raw.githubusercontent.com/{repo}/{ref}/{path}"
TREE_TTL = 24 * 60 * 60
# GitHub allows 60 unauthenticated API calls an hour. A listing that can't be refreshed (rate limit, outage)
# falls back to the last good copy, kept this long.
STALE_TTL = 30 * 24 * 60 * 60
FILE_TTL = 7 * 24 * 60 * 60
MAX_FILE_BYTES = 400_000


class DocsUnavailable(Exception):
    """GitHub couldn't be reached (or its rate limit is spent) and nothing usable is cached."""


@dataclass(frozen=True)
class TreeEntry:
    path: str  # relative to the listed directory
    is_dir: bool


class DocsClient:
    def __init__(self, http: httpx.AsyncClient, cache: ExercismCacheRepository, token: str = ""):
        self.http = http
        self.cache = cache
        self.token = token

    async def tree(self, repo: str, ref: str, path: str = "", *, recursive: bool = True) -> list[TreeEntry]:
        """Entries under `path` ("" = the repository root)."""
        key = f"docs-tree:{repo}@{ref}:{path}:{int(recursive)}"
        cached = await self.cache.get(key)
        if cached is None:
            try:
                cached = await self._fetch_tree(repo, ref, path, recursive)
            except DocsUnavailable:
                cached = await self.cache.get(key + ":stale")
                if cached is None:
                    raise
                logger.warning("Serving a stale listing of %s/%s", repo, path)
            else:
                await self.cache.put(key, cached, ttl_seconds=TREE_TTL)
                await self.cache.put(key + ":stale", cached, ttl_seconds=STALE_TTL)
        return [TreeEntry(e["path"], e["dir"]) for e in cached]

    async def _fetch_tree(self, repo: str, ref: str, path: str, recursive: bool) -> list[dict]:
        target = f"{ref}:{path}" if path else ref
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            response = await self.http.get(
                API.format(repo=repo, ref=target), params={"recursive": "1"} if recursive else None, headers=headers
            )
        except httpx.HTTPError as exc:
            raise DocsUnavailable(f"Couldn't reach GitHub: {type(exc).__name__}") from exc
        if response.status_code == 404:
            raise DocsUnavailable(f"{repo}@{ref} has no {path or 'root'} directory.")
        if response.status_code != 200:
            raise DocsUnavailable(f"GitHub returned {response.status_code} for {repo}")
        body = response.json()
        if body.get("truncated"):
            logger.warning("GitHub truncated the listing of %s/%s; some pages may be missing", repo, path)
        return [{"path": e["path"], "dir": e["type"] == "tree"} for e in body.get("tree", [])]

    async def text(self, repo: str, ref: str, path: str) -> str | None:
        """A file's text, or None if it doesn't exist (or is too big to be a doc page)."""
        key = f"docs-file:{repo}@{ref}:{path}"
        cached = await self.cache.get(key)
        if cached is not None:
            return cached["text"]
        try:
            response = await self.http.get(RAW.format(repo=repo, ref=ref, path=path))
        except httpx.HTTPError as exc:
            raise DocsUnavailable(f"Couldn't reach GitHub: {type(exc).__name__}") from exc
        if response.status_code == 404 or len(response.content) > MAX_FILE_BYTES:
            text = None
        elif response.status_code != 200:
            raise DocsUnavailable(f"GitHub returned {response.status_code} for {path}")
        else:
            text = response.text
        await self.cache.put(key, {"text": text}, ttl_seconds=FILE_TTL)
        return text
