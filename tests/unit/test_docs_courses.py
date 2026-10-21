"""Framework courses: planning topics from docs layouts, cleaning pages into lessons, and the service."""

import pytest

from app.core.errors import NotFoundError, ServiceUnavailableError
from app.domain.docs_courses import SPECS, DocsCourseSpec, page_url, parse_id, plan_topics, slugify
from app.domain.docs_markdown import code_includes, inline_code, to_markdown
from app.domain.live_lessons import trim_markdown
from app.integrations.docs import DocsUnavailable, TreeEntry
from app.services import docs_courses
from app.services.docs_courses import DocsCourseService

# --- planning topics -------------------------------------------------------------------------------------


def spec(**kwargs) -> DocsCourseSpec:
    base = dict(
        key="x", title="X", description="", language="python", repo="o/r", ref="main", license="MIT", ordering="nav"
    )
    return DocsCourseSpec(**{**base, **kwargs})


def test_ids_find_the_longest_framework_key():
    assert parse_id("fw-react") == ("react", "")
    assert parse_id("fw-data-science-ethics") == ("data-science", "ethics")
    assert parse_id("fw-nope-x") is None and parse_id("live-python") is None and parse_id("react") is None


def test_every_framework_teaches_a_language_the_platform_knows():
    from app.domain.languages import LANGUAGES

    assert all(s.language in LANGUAGES for s in SPECS.values())
    assert all(s.key == k for k, s in SPECS.items())


def test_slugs_ignore_ordering_prefixes_and_extensions():
    assert slugify("01-getting-started/02-project-structure") == "getting-started-project-structure"
    assert slugify("chapter1/2") == "chapter1-2"


def test_nav_order_titles_and_sections_come_from_the_navigation_file():
    nav = """
    - title: 0. Setup
      sections:
      - local: chapter0/1
        title: Introduction
    - title: 1. Models
      sections:
      - local: chapter1/1
        title: What is it
      - local: chapter1/2
        title: How it works
    - title: 9. Later
      sections:
      - local: chapter9/1
        title: Skipped
    """
    s = spec(
        root="c",
        file_template="{slug}.mdx",
        item_regex=r"- local:\s*(?P<slug>\S+)\s*\n\s*title:\s*(?P<title>.+)",
        section_regex=r"^\s*- title:\s*(?P<name>.+)$",
        include_sections=("0.", "1."),
    )
    files = ["c/chapter0/1.mdx", "c/chapter1/1.mdx", "c/chapter1/2.mdx", "c/chapter9/1.mdx"]
    topics = plan_topics(s, files, nav)
    assert [(t.slug, t.name, t.section) for t in topics] == [
        ("chapter0-1", "Introduction", "Setup"),
        ("chapter1-1", "What is it", "Models"),
        ("chapter1-2", "How it works", "Models"),
    ]
    assert [t.kind for t in topics] == ["doc"] * 3 and topics[0].path == "c/chapter0/1.mdx"


def test_nav_pages_missing_from_the_repo_and_duplicates_are_dropped_and_index_gets_a_name():
    s = spec(root="docs", item_regex=r"tutorial/(?P<slug>[\w-]+)\.md")
    nav = "tutorial/index.md\ntutorial/a.md\ntutorial/a.md\ntutorial/gone.md\ntutorial/b.md"
    topics = plan_topics(s, ["docs/index.md", "docs/a.md", "docs/b.md"], nav)
    assert [(t.slug, t.name) for t in topics] == [("index", "Introduction"), ("a", "A"), ("b", "B")]


def test_numbered_layouts_sort_naturally_and_keep_only_wanted_sections():
    s = spec(
        ordering="numbered",
        root="docs",
        page_regex=r"^(?P<section>\d+-[^/]+)/(?P<page>\d+-[^/]+)\.mdx?$",
        include_sections=("01-start",),
    )
    files = [
        "docs/01-start/10-last.mdx",
        "docs/01-start/02-second-page.mdx",
        "docs/01-start/01-first.mdx",
        "docs/01-start/index.mdx",
        "docs/02-other/01-x.mdx",
        "elsewhere/01-start/01-y.mdx",
    ]
    topics = plan_topics(s, files)
    assert [t.name for t in topics] == ["First", "Second page", "Last"]
    assert {t.section for t in topics} == {"Start"}


def test_lesson_folders_with_a_readme_become_topics_named_after_the_folder():
    s = spec(
        ordering="numbered",
        page_regex=r"^(?P<section>\d+-[^/]+)/(?P<page>\d+-[^/]+)/README\.md$",
    )
    files = ["2-Regression/1-Tools/README.md", "2-Regression/1-Tools/assignment.md", "1-Intro/1-what-is-ml/README.md"]
    assert [(t.name, t.section) for t in plan_topics(s, files)] == [("What is ml", "Intro"), ("Tools", "Regression")]


def test_explicit_pages_keep_their_order_and_skip_missing_ones():
    s = spec(ordering="explicit", root="d", file_template="{slug}.mdx", pages=("starter/a", "guide/b", "guide/gone"))
    topics = plan_topics(s, ["d/guide/b.mdx", "d/starter/a.mdx"])
    assert [(t.name, t.section) for t in topics] == [("A", "Starter"), ("B", "Guide")]


def test_a_course_is_capped_and_gets_a_rising_difficulty():
    s = spec(ordering="explicit", file_template="{slug}.md", pages=tuple(f"p{i:02d}" for i in range(50)), max_topics=30)
    topics = plan_topics(s, [f"p{i:02d}.md" for i in range(50)])
    assert len(topics) == 30 and topics[0].level == 1 and topics[-1].level == 10
    assert [t.level for t in topics] == sorted(t.level for t in topics)


def test_a_page_links_to_its_site_or_else_its_github_file():
    react = SPECS["react"]
    assert page_url(react, "src/content/learn/state.md") == "https://react.dev/learn/state"
    nextjs = SPECS["nextjs"]
    assert page_url(nextjs, "docs/01-app/01-getting-started/02-a.mdx") == "https://nextjs.org/docs/app/getting-started/a"
    ml = SPECS["scikit-learn"]
    assert page_url(ml, "1-Intro/1-x/README.md").startswith("https://github.com/microsoft/ML-For-Beginners/blob/main/")


# --- cleaning pages ---------------------------------------------------------------------------------------

PAGE = "https://site.dev/docs/page/"
IMG = "https://cdn.test/o/r@main/docs/"
PUB = "https://cdn.test/o/r@main/public/"


def clean(text, **kwargs):
    return to_markdown(text, page_url=PAGE, image_base=IMG, public_base=PUB, **kwargs)


def test_front_matter_gives_the_title_and_is_removed_along_with_mdx_plumbing():
    title, body = clean("---\ntitle: Hello World\n---\n\nimport A from './a'\n\n<!-- note -->\nText.\n")
    assert title == "Hello World" and body == "Text."


def test_first_heading_becomes_the_title_and_is_not_repeated():
    title, body = clean("# First Steps { #first-steps }\n\nBody.")
    assert title == "First Steps" and body == "Body."


def test_admonitions_become_quotes_and_components_keep_their_label():
    _, body = clean("/// tip | Pro tip\nUse it.\n///\n\n::: warning\nCareful\n:::\n\n<Pitfall>\nDon't.\n</Pitfall>")
    assert "> **Pro tip**" in body and "> Use it." in body
    assert "> **Warning**" in body and "> Careful" in body
    assert "**Watch out**" in body and "Don't." in body and "<Pitfall>" not in body


def test_components_vanish_but_their_text_stays():
    _, body = clean("<Intro>\n\nReact is a library.\n\n</Intro>\n\n<Sandpack>\n\n```js\nx()\n```\n\n</Sandpack>")
    assert "React is a library." in body and "```js\nx()\n```" in body
    assert "Intro" not in body.replace("React is a library.", "") and "Sandpack" not in body


def test_illustrations_and_diagrams_become_images_on_the_cdn():
    _, body = clean('<Illustration src="/images/a.png" alt="A cat" />\n\n<Diagram name="tree" alt="A tree" height={1}>x</Diagram>')
    assert f"![A cat]({PUB}images/a.png)" in body
    assert f"![A tree]({PUB}images/docs/diagrams/tree.png)" in body


def test_images_and_links_resolve_against_the_right_base():
    _, body = clean('![a](img/a.png) ![b](/img/b.png) ![c](https://x/c.png)\n\n[l](../other/) [r](/abs) [h](https://x) [a](#frag) [v](/docs/{{version}}/x)', version="12.x")
    assert f"![a]({IMG}img/a.png)" in body
    assert f"![b]({PUB}img/b.png)" in body and "![c](https://x/c.png)" in body
    assert "[l](https://site.dev/docs/other/)" in body and "[r](https://site.dev/abs)" in body
    assert "[h](https://x)" in body and "[a](#frag)" in body and "[v](https://site.dev/docs/12.x/x)" in body


def test_html_images_become_markdown_and_code_is_never_touched():
    text = '<img src="pic.png" alt="Pic">\n\n```jsx\n<Link href="/x">Array<string></Link>\n```\n\nUse `<Link>` or `List<T>` here.'
    _, body = clean(text)
    assert f"![Pic]({IMG}pic.png)" in body
    assert '<Link href="/x">Array<string></Link>' in body
    assert "`<Link>`" in body and "`List<T>`" in body


def test_terminal_colour_markup_is_stripped_only_from_terminal_blocks():
    text = '```console\n$ <font color="#fff">run</font> <span style="x">it</span>\n```\n\n```html\n<span>keep</span>\n```'
    _, body = clean(text)
    assert "$ run it" in body and "<span>keep</span>" in body


def test_a_leading_table_of_contents_and_heading_anchors_are_dropped():
    _, body = clean("# T\n\n- [A](#a)\n    - [B](#b)\n\n## A {#a}\n\nText\n\n## B {/*b*/}\n")
    assert body.startswith("## A") and "{#a}" not in body and "{/*b*/}" not in body


def test_code_includes_are_inlined_from_fetched_files():
    text = "Intro\n\n{* ../../docs_src/first/app.py hl[1] *}\n\n{! ../../docs_src/old/x.py !}\n\n{* ../../docs_src/missing.py *}"
    assert [n for _, n in code_includes(text)] == ["first/app.py", "old/x.py", "missing.py"]
    out = inline_code(text, {"first/app.py": "print(1)\n", "old/x.py": "x = 2"})
    assert "```python\nprint(1)\n```" in out and "```python\nx = 2\n```" in out and "{*" not in out and "{!" not in out


def test_trimming_never_ends_inside_a_code_block():
    text = "intro\n\n```py\n" + "x = 1\n" * 400 + "```\n\nafter"
    out = trim_markdown(text, limit=500)
    assert out.count("```") % 2 == 0 and out.endswith("…")


# --- the service ------------------------------------------------------------------------------------------


class FakeDocs:
    def __init__(self, files, texts, down=False):
        self.files, self.texts, self.down, self.tree_calls = files, texts, down, 0

    async def tree(self, repo, ref, path="", *, recursive=True):
        self.tree_calls += 1
        if self.down:
            raise DocsUnavailable("rate limited")
        prefix = f"{path}/" if path else ""
        return [TreeEntry(f.removeprefix(prefix), False) for f in self.files if f.startswith(prefix)]

    async def text(self, repo, ref, path):
        if self.down:
            raise DocsUnavailable("offline")
        return self.texts.get(path)


@pytest.fixture(autouse=True)
def _fresh_memo():
    docs_courses.clear_memo()
    yield
    docs_courses.clear_memo()


REACT_FILES = [f"src/content/learn/page-{i}.md" for i in range(8)]
REACT_NAV = "\n".join(f'{{"title": "Page {i}", "path": "/learn/page-{i}"}},' for i in range(8))
REACT_TEXTS = {
    "src/sidebarLearn.json": REACT_NAV,
    "src/content/learn/page-0.md": "---\ntitle: Page 0\n---\n\nHello **world**.\n\n![d](/images/d.png)\n",
}


def service(**kwargs):
    return DocsCourseService(FakeDocs(REACT_FILES, REACT_TEXTS, **kwargs))


async def test_a_framework_course_is_built_from_its_docs_and_remembered():
    svc = service()
    live = await svc.course("react")
    assert live.course.id == "fw-react" and live.course.kind == "framework" and live.course.language == "javascript"
    assert len(live.topics) == 8 and live.course.modules and live.course.total_xp > 0
    await svc.course("react")
    assert svc.docs.tree_calls == 1


async def test_requests_that_arrive_together_share_one_build():
    import asyncio

    svc = service()
    first, second = await asyncio.gather(svc.course("react"), svc.course("react"))
    assert first is second and svc.docs.tree_calls == 1


async def test_a_docs_page_becomes_a_lesson_with_images_on_the_cdn_and_a_credit():
    svc = service()
    live = await svc.course("react")
    lesson = await svc.lesson(live, "fw-react-page-0")
    assert lesson.title == "Page 0" and lesson.concept == "React Page 0" and lesson.exercise is None
    assert lesson.explanation == "Hello world."
    assert "![d](https://cdn.jsdelivr.net/gh/reactjs/react.dev@main/public/images/d.png)" in lesson.live_content
    assert lesson.live_source_name == "React docs · CC BY 4.0" and lesson.live_source_url == "https://react.dev/learn/page-0"
    assert lesson.module_id == "fw-react-m1" and lesson.course_id == "fw-react"


async def test_missing_pages_are_not_found_and_an_outage_is_unavailable():
    svc = service()
    live = await svc.course("react")
    with pytest.raises(NotFoundError):
        await svc.lesson(live, "fw-react-page-1")  # listed, but no text
    with pytest.raises(NotFoundError):
        await svc.lesson(live, "fw-react-nope")
    docs_courses.clear_memo()
    with pytest.raises(ServiceUnavailableError):
        await service(down=True).course("react")
    assert await service(down=True).courses() == []


async def test_unknown_keys_and_other_ids_have_no_course():
    svc = service()
    assert await svc.course("cobol") is None
    assert await svc.for_id("live-python") is None
    assert (await svc.for_id("fw-react-page-3")).course.id == "fw-react"


def test_index_pages_link_to_their_section_and_empty_links_vanish_from_summaries():
    from app.domain.live_lessons import plain_intro

    assert page_url(SPECS["react"], "src/content/learn/index.md") == "https://react.dev/learn/"
    assert page_url(SPECS["fastapi"], "docs/en/docs/tutorial/index.md") == "https://fastapi.tiangolo.com/tutorial/"
    assert plain_intro('---\n\n[![v](https://i/t.jpg)](https://youtu.be/x "Title")\n\nReal text here.') == "Real text here."
