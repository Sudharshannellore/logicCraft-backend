"""Turns a documentation page (Markdown, MDX, MkDocs, VitePress flavours) into plain Markdown a lesson can show.

Open-source docs are written for their own site generators: MDX components, admonition fences, relative
image links. This keeps the teaching text and code, converts the few constructs worth keeping (callouts,
diagrams) and drops the rest. Fenced code and inline code are never touched. No I/O.
"""

import re
from urllib.parse import urljoin

_FENCE = re.compile(r"^(```|~~~)", re.M)
_INLINE_CODE = re.compile(r"(`+[^`\n]*`+)")
_FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
_TITLE_LINE = re.compile(r"^title:\s*(.+?)\s*$", re.M)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_IMPORT_EXPORT = re.compile(r"^(?:import|export)\s.*$", re.M)
_HEADING_ANCHOR = re.compile(r"[ \t]*(?:\{#[\w-]+\}|\{/\*[^*]*\*/\}|\[\[[\w-]+\]\])[ \t]*$", re.M)
_TITLE_ANCHOR = re.compile(r"\s*(?:\{\s*#[\w-]+\s*\}|\[\[[\w-]+\]\])\s*$")
# A page that opens with its own table of contents (a list of `#anchor` links).
_LEADING_TOC = re.compile(r"\A(?:[ \t]*[-*] \[[^\]]+\]\(#[^)]*\)[ \t]*\n)+\s*")
_TERMINAL_MARKUP = re.compile(r"</?(?:font|span|u|b|i|strong|em)\b[^>]*>")
_TERMINAL_FENCE = re.compile(r"^(?:```|~~~)\s*(?:console|shell|terminal|text|bash|sh)\b", re.I)
_IMAGE = re.compile(r'(!\[[^\]]*\]\()\s*([^)\s]+)((?:\s+"[^"]*")?\))')
_HTML_IMG = re.compile(r"<img\b[^>]*?>", re.I)
_LINK = re.compile(r'(?<!!)(\[[^\]]*\]\()\s*([^)\s]+)((?:\s+"[^"]*")?\))')
_ATTR = r'{name}\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|\{{"([^"]*)"\}})'

# Components that carry a label worth keeping, and what to call it.
_LABELLED = {
    "note": "Note",
    "tip": "Tip",
    "pitfall": "Watch out",
    "gotcha": "Watch out",
    "warning": "Warning",
    "caution": "Warning",
    "danger": "Warning",
    "info": "Note",
    "alert": "Note",
    "deepdive": "Deep dive",
    "recap": "Recap",
    "youwilllearn": "You will learn",
    "challenge": "Challenge",
    "solution": "Solution",
    "hint": "Hint",
}
_ADMONITION_OPEN = re.compile(r"^(?:///|:::)\s*([\w-]+)\s*(?:\|\s*|\s+)?(.*?)\s*$")
_ADMONITION_CLOSE = re.compile(r"^(?:///|:::)\s*$")
_COMPONENT_TAG = re.compile(r"</?([A-Z][A-Za-z0-9.]*)\b(?:[^<>]|=>)*?/?>", re.S)
_HTML_TAG = re.compile(r"</?(?:div|span|p|br|center|section|article|aside|figure|figcaption|sup|sub|table|thead|tbody|tr|td|th|a|picture|source)\b[^<>]*>", re.I)
_SUMMARY = re.compile(r"<summary[^>]*>(.*?)</summary>", re.S | re.I)
_DETAILS = re.compile(r"</?details[^>]*>", re.I)
_CODE_INCLUDE = re.compile(r"\{\*\s*(?:\.\./)*docs_src/(?P<file>\S+?)(?:\s+(?:hl|ln)\[[^\]]*\])*\s*\*\}|\{!\s*(?:\.\./)*docs_src/(?P<old>\S+?)\s*!\}")


def _attr(tag: str, name: str) -> str | None:
    match = re.search(_ATTR.format(name=name), tag)
    return next((g for g in match.groups() if g is not None), None) if match else None


def _split_fences(text: str) -> list[tuple[bool, str]]:
    """[(is_code, text)]: fenced code blocks and the prose around them."""
    parts: list[tuple[bool, str]] = []
    lines, buffer, fence = text.split("\n"), [], None
    for line in lines:
        marker = _FENCE.match(line.lstrip())
        if fence is None and marker:
            if buffer:
                parts.append((False, "\n".join(buffer)))
            buffer, fence = [line], marker.group(1)
        elif fence is not None and line.lstrip().startswith(fence):
            buffer.append(line)
            parts.append((True, "\n".join(buffer)))
            buffer, fence = [], None
        else:
            buffer.append(line)
    if buffer:
        parts.append((fence is not None, "\n".join(buffer)))
    return parts


def _admonitions(text: str) -> str:
    """`/// tip | Title` … `///` and `::: tip` … `:::` become block quotes with a bold label."""
    out, inside = [], False
    for line in text.split("\n"):
        if inside and _ADMONITION_CLOSE.match(line):
            inside = False
            continue
        opened = None if inside else _ADMONITION_OPEN.match(line)
        if opened and not _ADMONITION_CLOSE.match(line):
            kind, title = opened.group(1), opened.group(2)
            label = title or _LABELLED.get(kind.lower(), kind.capitalize())
            out += [f"> **{label}**", ">"]
            inside = True
            continue
        out.append(f"> {line}" if inside else line)
    return "\n".join(out)


def _components(text: str, public_base: str) -> str:
    """MDX components: illustrations become images, callouts a bold label, everything else is dropped."""

    def illustration(match: re.Match[str]) -> str:
        tag = match.group(0)
        src, alt = _attr(tag, "src"), _attr(tag, "alt") or ""
        return f"\n\n![{alt}]({src})\n\n" if src else ""

    def diagram(match: re.Match[str]) -> str:
        tag = match.group(0)
        name, alt = _attr(tag, "name"), _attr(tag, "alt") or ""
        return f"\n\n![{alt}](/images/docs/diagrams/{name}.png)\n\n" if name else ""

    text = re.sub(r"<Illustration\b[^>]*?/?>", illustration, text, flags=re.S)
    text = re.sub(r"<Diagram\b[^>]*?>", diagram, text, flags=re.S)

    def component(match: re.Match[str]) -> str:
        label = _LABELLED.get(match.group(1).lower())
        if label and not match.group(0).startswith("</") and not match.group(0).endswith("/>"):
            return f"\n\n**{label}**\n\n"
        return ""

    text = _COMPONENT_TAG.sub(component, text)
    text = _SUMMARY.sub(lambda m: f"\n\n**{re.sub(r'<[^>]+>', '', m.group(1)).strip()}**\n\n", text)
    text = _DETAILS.sub("", text)
    return _HTML_TAG.sub("", text)


def _prose(text: str, *, page_url: str, image_base: str, public_base: str, version: str) -> str:
    text = _COMMENT.sub("", text)
    text = _IMPORT_EXPORT.sub("", text)
    text = _admonitions(text)

    def html_image(match: re.Match[str]) -> str:
        tag = match.group(0)
        src = _attr(tag, "src")
        return f"![{_attr(tag, 'alt') or ''}]({src})" if src else ""

    text = _HTML_IMG.sub(html_image, text)
    text = _components(text, public_base)
    text = _HEADING_ANCHOR.sub("", text)

    def image(match: re.Match[str]) -> str:
        src = match.group(2)
        if re.match(r"(?:[a-z][a-z0-9+.-]*:|//)", src, re.I):
            return match.group(0)
        base = public_base if src.startswith("/") else image_base
        return f"{match.group(1)}{urljoin(base, src.lstrip('/') if src.startswith('/') else src)}{match.group(3)}"

    def link(match: re.Match[str]) -> str:
        target = match.group(2).replace("{{version}}", version)
        if target.startswith("#") or re.match(r"(?:[a-z][a-z0-9+.-]*:|//)", target, re.I):
            return f"{match.group(1)}{target}{match.group(3)}"
        return f"{match.group(1)}{urljoin(page_url, target)}{match.group(3)}"

    # Links before images: the link pattern skips `![`; each pass leaves the other's output alone.
    text = _LINK.sub(link, text)
    return _IMAGE.sub(image, text)


def to_markdown(
    text: str,
    *,
    page_url: str,
    image_base: str,
    public_base: str = "",
    version: str = "",
) -> tuple[str | None, str]:
    """(title, markdown). `image_base` resolves relative images; `public_base` resolves `/root-relative` ones;
    `page_url` resolves relative links so they open on the project's site."""
    text = text.replace("\r\n", "\n")
    title = None
    front = _FRONT_MATTER.match(text)
    if front:
        found = _TITLE_LINE.search(front.group(1))
        title = found.group(1).strip("'\"") if found else None
        text = text[front.end() :]

    pieces = []
    for is_code, part in _split_fences(text):
        if is_code:
            # FastAPI-style docs colour terminal output with HTML; a lesson wants just the text.
            pieces.append(_TERMINAL_MARKUP.sub("", part) if _TERMINAL_FENCE.match(part.lstrip()) else part)
            continue
        # Inline code spans are protected so `Array<string>` and `{{ x }}` survive.
        spans = _INLINE_CODE.split(part)
        stash: dict[str, str] = {}
        flat = ""
        for i, span in enumerate(spans):
            if i % 2:
                token = f"\x00{len(stash)}\x00"
                stash[token] = span
                flat += token
            else:
                flat += span
        flat = _prose(flat, page_url=page_url, image_base=image_base, public_base=public_base, version=version)
        for token, span in stash.items():
            flat = flat.replace(token, span)
        pieces.append(flat)
    body = "\n".join(pieces)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    title = _TITLE_ANCHOR.sub("", title) if title else title

    heading = re.match(r"#\s+(.+)", body)
    if heading:  # the lesson already shows its title
        title = _TITLE_ANCHOR.sub("", title or heading.group(1).strip())
        body = body[heading.end() :].lstrip("\n")
    return title, _LEADING_TOC.sub("", body)


def code_includes(text: str) -> list[tuple[str, str]]:
    """[(marker text, docs_src file)] for `{* ../../docs_src/x.py *}` includes (FastAPI-style docs)."""
    return [(m.group(0), m.group("file") or m.group("old")) for m in _CODE_INCLUDE.finditer(text)]


_LANGUAGES = {"py": "python", "js": "javascript", "ts": "typescript", "sh": "bash", "json": "json", "html": "html"}


def inline_code(text: str, files: dict[str, str]) -> str:
    """Replaces each include marker with the fetched file as a fenced code block (unfetched ones are dropped)."""
    for marker, name in code_includes(text):
        source = files.get(name)
        language = _LANGUAGES.get(name.rsplit(".", 1)[-1], "")
        block = f"```{language}\n{source.strip()}\n```" if source else ""
        text = text.replace(marker, block, 1)
    return text
