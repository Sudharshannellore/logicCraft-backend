"""Quiz questions made from a framework's own documentation. No I/O, no AI: every answer comes straight from the docs.

A question is a sentence from a lesson with one key term blanked out ("Call ____ to add a state variable"),
and the learner picks the term from four. Key terms are the `inline code` and **bold** words the authors chose
to stress, so a question always tests something the docs themselves treat as important. Distractors are other
key terms from the same material, of the same kind. Generation is deterministic: the same page always yields the
same questions, so grading can recompute them instead of storing anything.
"""

import hashlib
import random
import re
from dataclasses import dataclass

OPTIONS = 4
MIN_SENTENCE = 45
MAX_SENTENCE = 230
MIN_TERM = 2
MAX_TERM = 28

_FENCE = re.compile(r"(```|~~~).*?\1", re.S)
_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_HTML = re.compile(r"<[^>\n]+>")
_CODE = re.compile(r"`([^`\n]+)`")
_BOLD = re.compile(r"\*\*([^*\n]+)\*\*")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z`*\"'(])")
_WORDY = re.compile(r"[A-Za-z]")
# Labels and connectives that make a sentence depend on text we don't show.
_LABELS = {"note", "tip", "warning", "info", "example", "watch out", "deep dive", "recap", "hint", "caution", "check"}
_DANGLING_START = {
    "this", "that", "these", "those", "it", "its", "they", "then", "also", "however", "but", "so", "and", "here",
    "there", "now", "next", "finally", "otherwise", "instead", "thus", "therefore", "for", "tip", "note", "warning",
}
_FILE = re.compile(r"^\.?[\w-]+(\.[A-Za-z0-9]{1,6})+$")


@dataclass(frozen=True)
class Question:
    id: str
    prompt: str  # the sentence with `_____` where the term goes
    options: list[str]
    answer: int
    # The full sentence, shown after answering.
    explanation: str
    lesson_id: str
    kind: str  # "code" or "term"


@dataclass(frozen=True)
class _Candidate:
    sentence: str
    term: str
    kind: str
    lesson_id: str


def _plain(text: str) -> str:
    """Prose with links, images and HTML reduced to their text; inline code and bold marks are kept."""
    text = _IMAGE.sub("", text)
    text = _LINK.sub(r"\1", text)
    parts = re.split(r"(`[^`\n]*`)", text)  # tags inside backticks are code to keep, not markup to strip
    return "".join(part if part.startswith("`") else _HTML.sub("", part) for part in parts)


def _paragraphs(markdown: str) -> list[str]:
    prose = _FENCE.sub("\n\n", markdown)
    blocks = []
    for block in re.split(r"\n\s*\n", prose):
        block = block.strip()
        # Headings, tables, quotes' markers and block-level code are not sentences to quiz.
        if not block or block.startswith(("#", "|", "    ", "\t", "<")):
            continue
        block = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", block, flags=re.M)
        block = re.sub(r"^>\s?", "", block, flags=re.M)
        blocks.append(" ".join(_plain(block).split()))
    return blocks


def _usable_term(term: str) -> bool:
    term = term.strip()
    if not (MIN_TERM <= len(term) <= MAX_TERM) or not _WORDY.search(term) or term.lower() in _LABELS:
        return False
    return term.count(" ") <= 2 and not term.startswith(("http", "/", "<", "{"))


def shape(term: str, kind: str) -> str:
    """What sort of thing a term is, so distractors can be the same sort (a command among commands)."""
    if kind == "term":
        words = term.split()
        return f"{'Cap' if term[:1].isupper() else 'low'}{'-multi' if len(words) > 1 else ''}"
    if term[:1] in "\"'":
        return "string"
    if "/" in term:
        return "path"
    if " " in term:
        return "command"
    if term.endswith(")") and "(" in term:
        return "call"
    if ":" in term or term[:1] in "$@":
        return "prefixed"
    if _FILE.match(term) or term.startswith("."):
        return "file"
    if "." in term:
        return "dotted"
    return "Cap" if term[:1].isupper() else "ident"


def _weak_bold(term: str) -> bool:
    """A bold word too ordinary to be a fair answer ("after", "locking")."""
    return " " not in term and "-" not in term and len(term) < 7 and not term[:1].isupper()


def _is_name_or_title(term: str) -> bool:
    words = term.split()
    return len(words) >= 2 and all(w[:1].isupper() for w in words)


def candidates(markdown: str, lesson_id: str) -> list[_Candidate]:
    """Every (sentence, blankable term) pair the text offers."""
    found: list[_Candidate] = []
    for paragraph in _paragraphs(markdown):
        for sentence in _SENTENCE_END.split(paragraph):
            sentence = sentence.strip()
            first_word = re.sub(r"[^a-z]", "", sentence.split(" ", 1)[0].lower())
            if not MIN_SENTENCE <= len(sentence) <= MAX_SENTENCE or first_word in _DANGLING_START:
                continue
            for pattern, kind in ((_CODE, "code"), (_BOLD, "term")):
                for term in dict.fromkeys(t.strip() for t in pattern.findall(sentence)):
                    # A term that appears once can be blanked without ambiguity; any other terms stay in view.
                    if not _usable_term(term) or sentence.count(term) != 1:
                        continue
                    if kind == "term" and (
                        _is_name_or_title(term) or _weak_bold(term) or sentence.lstrip("*").startswith(term)
                    ):
                        continue  # a person's name, a title, an ordinary word, or a bold label opening the sentence
                    found.append(_Candidate(sentence, term, kind, lesson_id))
    return found


def key_terms(markdown: str) -> dict[str, set[str]]:
    """All `code` and **bold** terms in a page, by kind: the pool distractors are drawn from."""
    prose = _FENCE.sub(" ", markdown)
    return {
        "code": {t.strip() for t in _CODE.findall(prose) if _usable_term(t)},
        "term": {t.strip() for t in _BOLD.findall(prose) if _usable_term(t)},
    }


def _seed(*parts: str) -> int:
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:12], 16)


def _distractors(cand: _Candidate, pool: set[str], rng: random.Random) -> list[str]:
    """Other terms of the same sort as the answer, similar in length. Fewer than three means no fair question."""
    sentence = cand.sentence.lower()
    wanted = shape(cand.term, cand.kind)
    usable = sorted(
        t
        for t in pool
        if t.lower() != cand.term.lower()
        and t.lower() not in sentence
        and "\n" not in t
        and shape(t, cand.kind) == wanted
        and not (cand.kind == "term" and _is_name_or_title(t))
    )
    usable.sort(key=lambda t: (abs(len(t) - len(cand.term)) // 4, rng.random()))
    return usable[: OPTIONS - 1]


def make_questions(
    pages: dict[str, str],
    *,
    seed: str,
    count: int,
    per_page: int = 3,
    pool_pages: dict[str, str] | None = None,
) -> list[Question]:
    """Up to `count` questions across `pages` ({lesson id: Markdown}), spread over pages, in a stable order.

    `pool_pages` are extra material that only supplies wrong answers (a single short page has few terms).
    """
    pool: dict[str, set[str]] = {"code": set(), "term": set()}
    by_page: dict[str, list[_Candidate]] = {}
    for markdown in (pool_pages or {}).values():
        terms = key_terms(markdown)
        pool["code"] |= terms["code"]
        pool["term"] |= terms["term"]
    for lesson_id in sorted(pages):
        terms = key_terms(pages[lesson_id])
        pool["code"] |= terms["code"]
        pool["term"] |= terms["term"]
        by_page[lesson_id] = candidates(pages[lesson_id], lesson_id)

    rng = random.Random(_seed(seed))
    chosen: list[_Candidate] = []
    taken_terms: set[str] = set()
    taken_sentences: set[str] = set()
    # Round-robin over pages (shuffled by the seed) so one long page can't take every slot.
    order = sorted(by_page, key=lambda lid: _seed(seed, lid))
    queues = {lid: rng_shuffled(by_page[lid], _seed(seed, lid, "q"))[:per_page] for lid in order}
    while len(chosen) < count and any(queues.values()):
        for lid in order:
            while queues[lid]:
                cand = queues[lid].pop(0)
                key = f"{cand.kind}:{cand.term.lower()}"
                if key in taken_terms or cand.sentence in taken_sentences:
                    continue
                if len(_distractors(cand, pool[cand.kind], random.Random(0))) < OPTIONS - 1:
                    continue
                taken_terms.add(key)
                taken_sentences.add(cand.sentence)
                chosen.append(cand)
                break
            if len(chosen) >= count:
                break

    questions = []
    for n, cand in enumerate(chosen):
        local = random.Random(_seed(seed, cand.lesson_id, cand.term, "options"))
        options = [cand.term, *_distractors(cand, pool[cand.kind], local)]
        local.shuffle(options)
        marked = re.sub(r"`|\*\*", "", cand.sentence)
        blank = cand.sentence.replace(f"`{cand.term}`", "_____", 1).replace(f"**{cand.term}**", "_____", 1)
        questions.append(
            Question(
                id=f"q{n + 1}-{_seed(seed, cand.lesson_id, cand.term) % 10**6:06d}",
                prompt=re.sub(r"`|\*\*", "", blank),
                options=options,
                answer=options.index(cand.term),
                explanation=marked,
                lesson_id=cand.lesson_id,
                kind=cand.kind,
            )
        )
    return questions


def rng_shuffled[T](items: list[T], seed: int) -> list[T]:
    shuffled = list(items)
    random.Random(seed).shuffle(shuffled)
    return shuffled
