"""Job descriptions arrive as HTML. They're shown as Markdown (the frontend never renders raw HTML)."""

import re
from html import unescape
from html.parser import HTMLParser

MAX_CHARS = 20_000
_SKIP = {"script", "style", "noscript", "iframe", "svg", "head", "title", "form", "button"}
_BLOCK = {"p", "div", "section", "article", "header", "footer", "table", "tr", "blockquote"}


class _ToMarkdown(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0
        self.lists: list[list[int]] = []  # one entry per open list: [is_ordered, counter]
        self.href: str | None = None
        self.link_text: list[str] = []

    def _newline(self, blank: bool = True) -> None:
        self.out.append("\n\n" if blank else "\n")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in _BLOCK:
            self._newline()
        elif tag == "br":
            self._newline(blank=False)
        elif re.fullmatch(r"h[1-6]", tag):
            self._newline()
            self.out.append("### ")
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag in ("ul", "ol"):
            self.lists.append([tag == "ol", 0])
            self._newline()
        elif tag == "li":
            self._newline(blank=False)
            depth = max(0, len(self.lists) - 1)
            if self.lists and self.lists[-1][0]:
                self.lists[-1][1] += 1
                self.out.append(f"{'   ' * depth}{self.lists[-1][1]}. ")
            else:
                self.out.append(f"{'   ' * depth}- ")
        elif tag == "a":
            href = dict(attrs).get("href") or ""
            self.href = href if href.startswith(("https://", "http://")) else None
            self.link_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in _BLOCK or re.fullmatch(r"h[1-6]", tag):
            self._newline()
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag in ("ul", "ol"):
            if self.lists:
                self.lists.pop()
            self._newline()
        elif tag == "a" and self.href is not None:
            text = "".join(self.link_text).strip()
            self.out.append(f"[{text}]({self.href})" if text else "")
            self.href = None

    def handle_data(self, data: str) -> None:
        if self.skip:
            return
        text = re.sub(r"\s+", " ", data)
        # Characters Markdown would treat as syntax at the start of a line, or inline.
        text = re.sub(r"([\\`*_\[\]<>|])", r"\\\1", text)
        if self.href is not None:
            self.link_text.append(text)
        else:
            self.out.append(text)


def html_to_markdown(html: str) -> str:
    parser = _ToMarkdown()
    parser.feed(unescape(html) if "<" not in html else html)
    parser.close()
    text = "".join(parser.out)
    text = re.sub(r"\*\*\s*\*\*", "", text)  # empty bold from <strong></strong>
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+(?=[^\s\-\d])", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS].rsplit("\n", 1)[0] + "\n\n…"
    return text


def html_to_text(html: str) -> str:
    """Plain text, for matching and summaries."""
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(text)).strip()
