"""Framework courses: which open-source documentation to teach from, and how to turn it into topics. No I/O.

A framework course is a *source description*, not content. Each entry below says where a project's docs
live and how their order is known; the engine reads the repository live and builds the course. To add a
framework, add one `DocsCourseSpec` here (and the course shows up on its own).

Ordering comes from the docs themselves, in one of three ways:
  nav       a navigation file lists the pages in order (React's sidebar, FastAPI's mkdocs.yml, ...)
  numbered  files and folders carry numeric prefixes (Next.js `01-getting-started/02-project-structure.mdx`)
  explicit  a short list of pages, for small docs with no usable navigation
"""

import re
from dataclasses import dataclass
from typing import Literal

from app.domain.live_courses import RawTopic, ramp_levels

COURSE_PREFIX = "fw-"
MAX_TOPICS = 30

Ordering = Literal["nav", "numbered", "explicit"]
# How to find the candidate files: one recursive listing; a listing per matching section folder; or the
# matching folders alone (each holds one lesson file, named by `leaf`).
Listing = Literal["tree", "sections", "dirs"]


@dataclass(frozen=True)
class DocsCourseSpec:
    key: str
    title: str
    description: str
    language: str  # a course language id: scopes tutorials and supplies the zone-boss challenges
    repo: str
    ref: str
    license: str
    ordering: Ordering
    root: str = ""  # directory (in the repo) that the page paths below are relative to
    listing: Listing = "tree"
    dir_regex: str = ""
    leaf: str = ""
    # nav
    nav_file: str = ""
    item_regex: str = ""  # named groups: slug, title (optional)
    section_regex: str = ""  # named group: name
    file_template: str = "{slug}.md"  # a nav slug's file, under `root`
    # numbered
    page_regex: str = ""  # against paths under `root`; named groups: section (optional), page (optional)
    # explicit
    pages: tuple[str, ...] = ()
    # only these sections (name prefixes, as the docs name them)
    include_sections: tuple[str, ...] = ()
    max_topics: int = MAX_TOPICS
    # Where a page lives on the web ({path} = its clean path, {page} = the last part); "" = the GitHub file.
    site_template: str = ""
    site_origin: str = ""
    # Where root-relative image links (`/images/a.png`) are stored in the repo.
    public_dir: str = ""
    # `{* ../../docs_src/x.py *}` style includes are fetched from this repo directory and inlined.
    code_includes_dir: str = ""


SPECS: dict[str, DocsCourseSpec] = {
    spec.key: spec
    for spec in (
        DocsCourseSpec(
            key="react",
            title="React",
            description="Build user interfaces with components, state and effects, from React's own open-source docs.",
            language="javascript",
            repo="reactjs/react.dev",
            ref="main",
            license="CC BY 4.0",
            ordering="nav",
            root="src/content/learn",
            nav_file="src/sidebarLearn.json",
            item_regex=r'"title":\s*"(?P<title>[^"]+)",\s*"path":\s*"/learn(?:/(?P<slug>[\w-]+))?"',
            site_template="https://react.dev/learn/{path}",
            site_origin="https://react.dev",
            public_dir="public",
        ),
        DocsCourseSpec(
            key="nextjs",
            title="Next.js",
            description="Ship full-stack React apps with the App Router, server components and data fetching.",
            language="javascript",
            repo="vercel/next.js",
            ref="canary",
            license="MIT",
            ordering="numbered",
            root="docs/01-app",
            page_regex=r"^(?P<section>\d+-[^/]+)/(?P<page>\d+-[^/]+)\.mdx?$",
            include_sections=("01-getting-started", "02-guides"),
            site_template="https://nextjs.org/docs/app/{path}",
            site_origin="https://nextjs.org",
            public_dir="public",
        ),
        DocsCourseSpec(
            key="svelte",
            title="Svelte",
            description="Write small, fast components with runes, reactive state and a compiler-first approach.",
            language="javascript",
            repo="sveltejs/svelte",
            ref="main",
            license="MIT",
            ordering="numbered",
            root="documentation/docs",
            page_regex=r"^(?P<section>\d+-[^/]+)/(?P<page>\d+-[^/]+)\.md$",
            include_sections=("01-introduction", "02-runes", "03-template-syntax"),
            site_template="https://svelte.dev/docs/svelte/{page}",
            site_origin="https://svelte.dev",
        ),
        DocsCourseSpec(
            key="express",
            title="Express",
            description="Build web servers and APIs on Node.js: routing, middleware, templates and error handling.",
            language="javascript",
            repo="expressjs/expressjs.com",
            ref="main",
            license="CC BY 4.0",
            ordering="explicit",
            root="src/content/docs/en/4x",
            file_template="{slug}.mdx",
            pages=(
                "starter/installing",
                "starter/hello-world",
                "starter/generator",
                "starter/basic-routing",
                "starter/static-files",
                "guide/routing",
                "guide/writing-middleware",
                "guide/using-middleware",
                "guide/using-template-engines",
                "guide/error-handling",
                "guide/debugging",
                "guide/behind-proxies",
            ),
            site_template="https://expressjs.com/en/{path}.html",
            site_origin="https://expressjs.com",
        ),
        DocsCourseSpec(
            key="fastapi",
            title="FastAPI",
            description="Build fast, typed Python APIs: paths, validation, dependencies and security.",
            language="python",
            repo="tiangolo/fastapi",
            ref="master",
            license="MIT",
            ordering="nav",
            root="docs/en/docs/tutorial",
            nav_file="docs/en/mkdocs.yml",
            item_regex=r"tutorial/(?P<slug>[\w-]+)\.md",
            site_template="https://fastapi.tiangolo.com/tutorial/{path}/",
            site_origin="https://fastapi.tiangolo.com",
            public_dir="docs/en/docs",
            code_includes_dir="docs_src",
        ),
        DocsCourseSpec(
            key="laravel",
            title="Laravel",
            description="Build PHP web applications with routing, controllers, Blade views and Eloquent.",
            language="php",
            repo="laravel/docs",
            ref="13.x",
            license="MIT",
            ordering="nav",
            root="",
            nav_file="documentation.md",
            item_regex=r"\[(?P<title>[^\]]+)\]\(/docs/\{\{version\}\}/(?P<slug>[\w-]+)\)",
            section_regex=r"^- ## (?P<name>.+)$",
            include_sections=("Getting Started", "Architecture Concepts", "The Basics"),
            site_template="https://laravel.com/docs/13.x/{path}",
            site_origin="https://laravel.com",
        ),
        DocsCourseSpec(
            key="huggingface",
            title="Hugging Face Transformers",
            description="Use pretrained transformer models: pipelines, tokenizers, fine-tuning and sharing.",
            language="python",
            repo="huggingface/course",
            ref="main",
            license="Apache-2.0",
            ordering="nav",
            root="chapters/en",
            nav_file="chapters/en/_toctree.yml",
            item_regex=r"- local:\s*(?P<slug>\S+)\s*\n\s*title:\s*(?P<title>.+)",
            section_regex=r"^- title:\s*(?P<name>.+)$",
            file_template="{slug}.mdx",
            include_sections=("1.", "2.", "3.", "4."),
            site_template="https://huggingface.co/learn/llm-course/{path}",
            site_origin="https://huggingface.co",
        ),
        DocsCourseSpec(
            key="scikit-learn",
            title="Machine Learning with scikit-learn",
            description="Classical machine learning from regression to clustering, with Microsoft's open ML curriculum.",
            language="python",
            repo="microsoft/ML-For-Beginners",
            ref="main",
            license="MIT",
            ordering="numbered",
            listing="sections",
            dir_regex=r"^\d+-[^/]+$",
            page_regex=r"^(?P<section>\d+-[^/]+)/(?P<page>\d+-[^/]+)/README\.md$",
        ),
        DocsCourseSpec(
            key="data-science",
            title="Data Science with pandas",
            description="Work with data end to end: cleaning, statistics, visualisation and the data science lifecycle.",
            language="python",
            repo="microsoft/Data-Science-For-Beginners",
            ref="main",
            license="MIT",
            ordering="numbered",
            listing="sections",
            dir_regex=r"^\d+-[^/]+$",
            page_regex=r"^(?P<section>\d+-[^/]+)/(?P<page>\d+-[^/]+)/README\.md$",
        ),
        DocsCourseSpec(
            key="generative-ai",
            title="Generative AI Apps",
            description="Build applications on large language models: prompts, RAG, agents and responsible AI.",
            language="python",
            repo="microsoft/generative-ai-for-beginners",
            ref="main",
            license="MIT",
            ordering="numbered",
            listing="dirs",
            dir_regex=r"^\d+-[^/]+$",
            leaf="README.md",
            page_regex=r"^(?P<page>\d+-[^/]+)/README\.md$",
        ),
    )
}


# --- ids ----------------------------------------------------------------------------------------------


def course_id(key: str) -> str:
    return f"{COURSE_PREFIX}{key}"


def parse_id(item_id: str) -> tuple[str, str] | None:
    """`fw-react-state` → ("react", "state"); `fw-react` → ("react", ""). None unless a known framework."""
    if not item_id.startswith(COURSE_PREFIX):
        return None
    rest = item_id.removeprefix(COURSE_PREFIX)
    for key in sorted(SPECS, key=len, reverse=True):  # `data-science` before a hypothetical `data`
        if rest == key:
            return key, ""
        if rest.startswith(key + "-"):
            return key, rest[len(key) + 1 :]
    return None


# --- turning docs into topics ---------------------------------------------------------------------------


def _natural(text: str) -> list:
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", text)]


def prettify(name: str) -> str:
    """`02-server-and-client-components` → "Server and client components"."""
    words = re.sub(r"^\d+[-_.]\s*", "", name).replace("-", " ").replace("_", " ").strip()
    return words[:1].upper() + words[1:] if words else name


def slugify(path: str) -> str:
    """A URL-safe topic id from a page path, ignoring numeric ordering prefixes: stable if pages are reordered."""
    parts = [re.sub(r"^\d+[-_.]\s*", "", part) for part in path.split("/")]
    return re.sub(r"[^a-z0-9]+", "-", "-".join(parts).lower()).strip("-")


def clean_path(path: str) -> str:
    """A page's path without its extension, numeric prefixes or `README`: `01-start/02-a.mdx` → `start/a`."""
    stem = re.sub(r"(?:/README)?\.mdx?$", "", path)
    return "/".join(re.sub(r"^\d+[-_.]\s*", "", part) for part in stem.split("/"))


def _in_scope(section: str | None, spec: DocsCourseSpec) -> bool:
    if not spec.include_sections:
        return True
    return section is not None and any(section.startswith(prefix) for prefix in spec.include_sections)


def _under(root: str, path: str) -> str | None:
    if not root:
        return path
    return path.removeprefix(root + "/") if path.startswith(root + "/") else None


def _nav_pages(spec: DocsCourseSpec, nav_text: str) -> list[tuple[str, str | None, str | None]]:
    """[(slug, title, section as the docs write it)] in the navigation file's order."""
    events: list[tuple[int, str, re.Match[str]]] = [
        (m.start(), "item", m) for m in re.finditer(spec.item_regex, nav_text, re.M)
    ]
    if spec.section_regex:
        events += [(m.start(), "section", m) for m in re.finditer(spec.section_regex, nav_text, re.M)]
    section: str | None = None
    pages = []
    for _, kind, match in sorted(events, key=lambda e: e[0]):
        if kind == "section":
            section = match.group("name").strip().strip("'\"")
            continue
        groups = match.groupdict()
        title = (groups.get("title") or "").strip().strip("'\"") or None
        pages.append((match.group("slug") or "index", title, section))
    return pages


def _name(slug: str) -> str:
    last = slug.rsplit("/", 1)[-1]
    return "Introduction" if last == "index" else prettify(last)


def plan_topics(spec: DocsCourseSpec, files: list[str], nav_text: str | None = None) -> list[RawTopic]:
    """The course's topics in order. `files` are repo-root-relative paths of the candidate files that exist."""
    available = set(files)
    found: list[tuple[str, str, str | None, str]] = []  # (slug-source path, title, section, repo path)

    if spec.ordering == "nav":
        for slug, title, section in _nav_pages(spec, nav_text or ""):
            if not _in_scope(section, spec):
                continue
            path = f"{spec.root}/{spec.file_template.format(slug=slug)}".lstrip("/")
            if path in available:
                shown = re.sub(r"^\d+\.\s*", "", section) if section else None
                found.append((slug, title or _name(slug), shown, path))
    elif spec.ordering == "explicit":
        for page in spec.pages:
            path = f"{spec.root}/{spec.file_template.format(slug=page)}".lstrip("/")
            if path in available:
                section = prettify(page.split("/")[0]) if "/" in page else None
                found.append((page, _name(page), section, path))
    else:
        pattern = re.compile(spec.page_regex)
        for path in sorted(available, key=_natural):
            rel = _under(spec.root, path)
            match = pattern.match(rel) if rel is not None else None
            if not match:
                continue
            groups = match.groupdict()
            raw_section = groups.get("section")
            if not _in_scope(raw_section, spec) or (groups.get("page") or "").lower().startswith("index"):
                continue
            page = groups.get("page") or rel
            found.append((rel, prettify(page), prettify(raw_section) if raw_section else None, path))

    seen: set[str] = set()
    unique = []
    for source, title, section, path in found:
        slug = slugify(clean_path(source))
        if not slug or slug in seen:
            continue
        seen.add(slug)
        unique.append((slug, title, section, path))
    unique = unique[: spec.max_topics]
    levels = ramp_levels(len(unique))
    return [
        RawTopic(slug=slug, name=title, kind="doc", level=level, path=path, section=section)
        for (slug, title, section, path), level in zip(unique, levels, strict=True)
    ]


def page_url(spec: DocsCourseSpec, path: str) -> str:
    """Where a page lives on the web, for the source link (the GitHub file if the project has no site)."""
    rel = _under(spec.root, path) or path
    if spec.site_template:
        cleaned = clean_path(rel)
        if cleaned.rsplit("/", 1)[-1] == "index":  # a section's index page lives at the section's own address
            cleaned = cleaned.rsplit("/", 1)[0] if "/" in cleaned else ""
        url = spec.site_template.format(path=cleaned, page=cleaned.rsplit("/", 1)[-1])
        return re.sub(r"(?<!:)/{2,}", "/", url)
    return f"https://github.com/{spec.repo}/blob/{spec.ref}/{path}"
