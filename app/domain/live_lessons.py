"""Tidying a live lesson's Markdown: trimming it for display and taking a plain-text summary. No I/O."""

import re
from urllib.parse import urljoin

INTRO_CHARS = 600
MAX_MARKDOWN_CHARS = 8_000


def trim_markdown(markdown: str, limit: int = MAX_MARKDOWN_CHARS) -> str:
    """The text a lesson can show: front-matter removed and capped at a paragraph boundary."""
    text = re.sub(r"\A---\n.*?\n---\n", "", markdown, flags=re.S).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit("\n\n", 1)[0]
    while cut.count("```") % 2:  # never end inside a code block, or the rest of the page would render as code
        cut = cut[: cut.rindex("```")].rstrip()
    return cut.rstrip() + "\n\n…"


def plain_intro(markdown: str) -> str:
    """The opening prose as plain text (no headings, code or links), for places that don't render Markdown."""
    text = re.sub(r"```.*?```", "", markdown, flags=re.S)
    text = re.sub(r"^\s*-{3,}\s*$", "", text, flags=re.M)  # horizontal rules
    text = re.sub(r"\[\s*\]\([^)]*\)", "", text)  # a link with nothing to click: a video thumbnail whose image was dropped
    text = re.sub(r"!?\[[^\]]*\]\([^)]*\)\s*$", lambda m: "" if m.group(0).lstrip().startswith(("![", "[]")) else m.group(0), text, flags=re.M)
    paragraphs: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith(("#", ">", "|", "- ", "* ", "1.")) or re.match(r"\[[^\]]+\]:\s", block):
            continue  # headings, quotes, tables, lists and `[ref]: url` link definitions
        block = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", block)
        block = re.sub(r"\[([^\]]+)\](?:\([^)]*\)|\[[^\]]*\])", r"\1", block)  # inline and reference links
        block = re.sub(r"[`*_]", "", block)
        block = re.sub(r"\[\s*\]\([^)]*\)", "", block)  # the leftover of a video thumbnail whose image was dropped
        if not block.strip():
            continue
        paragraphs.append(" ".join(block.split()))
        if sum(len(p) for p in paragraphs) >= INTRO_CHARS:
            break
    intro = " ".join(paragraphs)
    if len(intro) <= INTRO_CHARS:
        return intro
    window = intro[:INTRO_CHARS]
    ends = [m.end() for m in re.finditer(r"[.!?](?=\s)", window)]
    return window[: ends[-1]] if ends else window.rstrip() + "…"


_IMAGE = re.compile(r'(!\[[^\]]*\]\()([^)\s]+)((?:\s+"[^"]*")?\))')


def absolutize_images(markdown: str, base_url: str) -> str:
    """Points relative image links (`![](img/a.png)`) at `base_url`, so they load outside the source repository."""

    def fix(match: re.Match[str]) -> str:
        target = match.group(2)
        if re.match(r"(?:[a-z][a-z0-9+.-]*:|//|#)", target, re.I):
            return match.group(0)
        return f"{match.group(1)}{urljoin(base_url, target)}{match.group(3)}"

    return _IMAGE.sub(fix, markdown)
