"""Framework courses: React, Next.js, FastAPI, Laravel... built live from each project's open-source docs.

The recipe for each one is a `DocsCourseSpec` (app/domain/docs_courses.py). This service lists the docs
repository, plans the topics, and renders a page as a lesson on demand. Nothing is stored or seeded.
"""

import asyncio
import re
import time

from app.core.errors import AppError, NotFoundError, ServiceUnavailableError
from app.domain.docs_courses import (
    SPECS,
    DocsCourseSpec,
    course_id,
    page_url,
    parse_id,
    plan_topics,
)
from app.domain.docs_markdown import code_includes, inline_code, to_markdown
from app.domain.languages import LANGUAGES
from app.domain.live_courses import LiveCourse, assemble_course
from app.domain.live_lessons import plain_intro, trim_markdown
from app.integrations.docs import DocsClient, DocsUnavailable
from app.schemas.learning import Lesson

MEMO_SECONDS = 300
MAX_SECTION_LISTINGS = 12
DOC_MAX_CHARS = 30_000
CDN = "https://cdn.jsdelivr.net/gh/{repo}@{ref}/"  # serves images with the right content type

# course key -> (when built, course or None). Shared by every request in this process.
_memo: dict[str, tuple[float, LiveCourse | None]] = {}
_building: dict[str, asyncio.Task] = {}


def clear_memo() -> None:
    _memo.clear()


def _join(*parts: str) -> str:
    return "/".join(p.strip("/") for p in parts if p)


class DocsCourseService:
    def __init__(self, docs: DocsClient):
        self.docs = docs

    # --- Courses ----------------------------------------------------------------------------------------

    async def _files(self, spec: DocsCourseSpec) -> list[str]:
        """Repo-relative paths of the candidate pages, per the spec's listing mode."""
        if spec.listing == "tree":
            entries = await self.docs.tree(spec.repo, spec.ref, spec.root, recursive=True)
            return [_join(spec.root, e.path) for e in entries if not e.is_dir]
        top = await self.docs.tree(spec.repo, spec.ref, spec.root, recursive=False)
        dirs = [e.path for e in top if e.is_dir and re.match(spec.dir_regex, e.path)]
        if spec.listing == "dirs":  # one lesson file per folder: no need to list each one
            return [_join(spec.root, d, spec.leaf) for d in dirs]
        listings = await asyncio.gather(
            *(self.docs.tree(spec.repo, spec.ref, _join(spec.root, d), recursive=True) for d in dirs[:MAX_SECTION_LISTINGS])
        )
        return [_join(spec.root, d, e.path) for d, entries in zip(dirs, listings, strict=False) for e in entries if not e.is_dir]

    async def course(self, key: str) -> LiveCourse | None:
        if key not in SPECS:
            return None
        hit = _memo.get(key)
        if hit and time.monotonic() - hit[0] < MEMO_SECONDS:
            return hit[1]
        # Requests that arrive together share one build (and one round of GitHub calls).
        task = _building.get(key)
        if task is None:
            task = _building[key] = asyncio.ensure_future(self._build(key))
            task.add_done_callback(lambda _: _building.pop(key, None))
        return await asyncio.shield(task)

    async def _build(self, key: str) -> LiveCourse | None:
        spec = SPECS[key]
        try:
            files = await self._files(spec)
            nav = await self.docs.text(spec.repo, spec.ref, spec.nav_file) if spec.ordering == "nav" else None
        except DocsUnavailable as exc:
            raise ServiceUnavailableError("The documentation source can't be reached right now — try again in a minute.") from exc
        built = assemble_course(
            cid=course_id(key),
            title=spec.title,
            world=f"{spec.title} Realm",
            description=spec.description,
            language_id=spec.language,
            language_name=LANGUAGES[spec.language].name,
            kind="framework",
            topics=plan_topics(spec, files, nav),
        )
        _memo[key] = (time.monotonic(), built)
        return built

    async def courses(self) -> list[LiveCourse]:
        """Every framework course; one whose docs can't be read right now is left out."""

        async def one(key: str) -> LiveCourse | None:
            try:
                return await self.course(key)
            except AppError:
                return None

        built = await asyncio.gather(*(one(key) for key in SPECS))
        return [c for c in built if c]

    async def for_id(self, item_id: str) -> LiveCourse | None:
        """The framework course a course, zone or topic id belongs to; None for any other id (no I/O then)."""
        parsed = parse_id(item_id)
        return await self.course(parsed[0]) if parsed else None

    # --- Lessons ------------------------------------------------------------------------------------------

    async def lesson(self, live: LiveCourse, lesson_id: str) -> Lesson:
        topic = live.topics.get(lesson_id)
        spec = SPECS.get(live.course.id.removeprefix("fw-"))
        if topic is None or spec is None:
            raise NotFoundError("Lesson not found.")
        try:
            text = await self.docs.text(spec.repo, spec.ref, topic.path)
            if text is not None and spec.code_includes_dir:
                names = {name for _, name in code_includes(text)}
                fetched = await asyncio.gather(
                    *(self.docs.text(spec.repo, spec.ref, _join(spec.code_includes_dir, n)) for n in names)
                )
                text = inline_code(text, {n: t for n, t in zip(names, fetched, strict=True) if t})
        except DocsUnavailable as exc:
            raise ServiceUnavailableError("The documentation source can't be reached right now — try again in a minute.") from exc
        if text is None:
            raise NotFoundError(f'The "{topic.name}" page is no longer in the {spec.title} docs.')

        url = page_url(spec, topic.path)
        cdn = CDN.format(repo=spec.repo, ref=spec.ref)
        folder = topic.path.rsplit("/", 1)[0] + "/" if "/" in topic.path else ""
        _, markdown = to_markdown(
            text,
            page_url=url,
            image_base=cdn + folder,
            public_base=cdn + (spec.public_dir.strip("/") + "/" if spec.public_dir else ""),
            version=spec.ref,
        )
        content = trim_markdown(markdown, limit=DOC_MAX_CHARS)
        return Lesson(
            id=lesson_id,
            course_id=live.course.id,
            module_id=topic.module_id,
            title=topic.name,
            # What searches for tutorials and pictures: the framework's name makes "State" mean React state.
            concept=f"{spec.title} {topic.name}",
            explanation=plain_intro(content) or topic.name,
            live_content=content,
            live_source_name=f"{spec.title} docs · {spec.license}",
            live_source_url=url,
        )
