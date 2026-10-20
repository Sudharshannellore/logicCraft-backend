"""Quest AI mentor: question suggestions and replies for the coding board and lessons.

Rule-based stand-in for a model (ported from the frontend's questAi.ts). Keep the signatures
when swapping in a real LLM.
"""

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProblemContext:
    title: str
    description: str
    tags: list[str]
    hints: list[str]
    examples: list[dict]  # {input, output, explanation?}


@dataclass(frozen=True)
class LessonContext:
    title: str
    concept: str
    explanation: str
    analogy: str | None = None
    key_points: list[str] = field(default_factory=list)
    step: str | None = None
    try_hint: str | None = None


MentorContext = ProblemContext | LessonContext


def suggested_questions(ctx: MentorContext) -> list[str]:
    if isinstance(ctx, ProblemContext):
        return [
            f"Give me a hint for {ctx.title}",
            "What should my first step be?",
            "Why is my code failing the tests?",
            "Walk me through Example 1",
            "How do I handle edge cases here?",
            "What is the time complexity of the best approach?",
            "Is there a faster approach than brute force?",
            *(f"How does a {t.lower()} help in this problem?" for t in ctx.tags),
            "Explain the problem in simpler words",
            "Give me a similar problem to practice",
        ]
    c = ctx.concept.lower()
    return [
        *(["Give me a hint for the Try it exercise"] if ctx.step == "tryit" else []),
        *(["Help me think through the quiz"] if ctx.step == "quiz" else []),
        f"Explain {c} in simpler words",
        f"Show me a real-world example of {c}",
        "How does the code example work?",
        f"When should I use {c}?",
        f"What are common mistakes with {c}?",
        f"What is the time complexity of {c}?",
        f"What should I learn after {c}?",
    ]


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#]+", text.lower())


def _edit_distance(a: str, b: str) -> int:
    """Levenshtein distance, capped early — only used to forgive one-letter typos."""
    if abs(len(a) - len(b)) > 1:
        return 2
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        diag, prev[0] = prev[0], i
        for j in range(1, len(b) + 1):
            tmp = prev[j]
            prev[j] = min(prev[j] + 1, prev[j - 1] + 1, diag + (a[i - 1] != b[j - 1]))
            diag = tmp
    return prev[len(b)]


def _token_matches(token: str, word: str) -> bool:
    if word.startswith(token):
        return True
    if len(token) >= 4 and _edit_distance(token, word[: len(token)]) <= 1:
        return True
    return len(token) >= 4 and _edit_distance(token, word) <= 1


def match_suggestions(pool: list[str], text: str, limit: int = 4) -> list[str]:
    """Suggestions related to what's being typed, best match first."""
    tokens = [t for t in _words(text) if len(t) >= 2]
    if not tokens:
        return pool[:limit]
    scored = []
    for q in pool:
        q_words = _words(q)
        score = sum(1 for t in tokens if any(_token_matches(t, w) for w in q_words))
        if score:
            scored.append((score, q))
    scored.sort(key=lambda s: -s[0])
    return [q for _, q in scored[:limit]]


TAG_APPROACH = {
    "hash table": "store what you have seen in a hash map so each lookup is O(1) — one pass, O(n) time and O(n) space",
    "array": "a single pass with a running value (like a best-so-far) usually beats nested loops",
    "two pointers": "move a left and right pointer toward each other so each element is visited once — O(n)",
    "string": "count characters with a map or a fixed-size array instead of comparing every pair",
    "linked list": "use a slow and a fast pointer, or reverse pointers in place, for O(1) extra space",
    "stack": "push items as you scan and pop when a match closes them — one pass, O(n)",
    "binary search": "halve the search range every step — O(log n)",
    "recursion": "solve a smaller version of the problem and combine — watch the base case",
    "dynamic programming": "save answers to sub-problems in a table so nothing is computed twice",
    "sorting": "sort first (O(n log n)), then a single scan often finds the answer",
}


def _has(q: str, *keys: str) -> bool:
    return any(k in q for k in keys)


def _approach(tags: list[str]) -> tuple[str, str] | None:
    for tag in tags:
        if tag.lower() in TAG_APPROACH:
            return tag, TAG_APPROACH[tag.lower()]
    return None


def mentor_reply(question: str, ctx: MentorContext, turn: int = 0) -> str:
    """`turn` = how many questions were asked before, so repeated hint requests reveal the next hint."""
    q = question.lower()

    if isinstance(ctx, ProblemContext):
        approach = _approach(ctx.tags)
        ex = ctx.examples[0] if ctx.examples else None
        if _has(q, "hint", "stuck", "clue"):
            if ctx.hints:
                return f"Hint: {ctx.hints[turn % len(ctx.hints)]}"
            return "Think about what you need to remember as you scan the input once."
        if _has(q, "complex", "big o", "time", "space", "faster", "optimal", "brute", "efficient"):
            if approach:
                return f"Brute force compares every pair — O(n²). The {approach[0].lower()} approach is better: {approach[1]}."
            return "Start from brute force (often O(n²)), then ask: what am I recomputing? Caching it usually brings you to O(n) or O(n log n)."
        if _has(q, "edge", "corner"):
            return (
                "Check these before submitting: an empty or one-element input, duplicates, negative numbers and zero, "
                "and the largest input the constraints allow. Trace your code on each one."
            )
        if _has(q, "example", "walk", "trace") and ex:
            note = (
                ex.get("explanation") or "Trace your loop on it by hand and write down every variable after each step."
            )
            return f"Example 1: input {ex['input']} → output {ex['output']}. {note}"
        if _has(q, "fail", "wrong", "error", "bug", "not work", "doesn't"):
            return (
                "Run the failing test by hand: print your variables each iteration and compare with what you expect. "
                "Most failures here are off-by-one loop bounds, returning too early, or not handling duplicates."
            )
        if _has(q, "similar", "practice", "another"):
            if approach:
                return (
                    f"Practice the same {approach[0].lower()} pattern with another problem from the Practice list tagged "
                    f'"{approach[0]}". Solving 2–3 in a row makes the pattern stick.'
                )
            return "Open the Practice list and filter by the same topic — solving 2–3 problems with the same pattern makes it stick."
        if _has(q, "first step", "start", "begin", "approach"):
            extra = f" and notice how a {approach[0].lower()} could remember what you've seen" if approach else ""
            return (
                f"First, restate the goal in one sentence. Then solve Example 1 by hand{extra}. Only then write code."
            )
        if approach and any(t.lower() in q for t in ctx.tags):
            return f"Here a {approach[0].lower()} lets you {approach[1]}."
        if _has(q, "simple", "explain", "understand", "mean", "what is"):
            first = re.split(r"(?<=\.)\s", ctx.description)[0]
            return f"In plain words: {first} Focus on what goes in, what must come out, and the smallest example."
        idea = (
            f"the key idea is that a {approach[0].lower()} lets you {approach[1]}"
            if approach
            else "solve the first example by hand, then turn each step into code"
        )
        return f"Good question. For {ctx.title}, {idea}. Ask me for a hint if you want a nudge."

    c = ctx.concept.lower()
    if _has(q, "try it", "exercise", "hint"):
        return (
            ctx.try_hint
            or "Re-read the step's instructions, then change one line at a time and run it to see what happens."
        )
    if _has(q, "quiz"):
        first_point = ctx.key_points[0] if ctx.key_points else ""
        return f"Don't guess — rule options out. Which ones contradict what you just learned about {c}? {first_point}".strip()
    if _has(q, "real", "world", "example"):
        if ctx.analogy:
            return f"Think of it like this: {ctx.analogy}"
        return f"Apps use {c} all the time — caches, search, and settings lookups are common places to find it."
    if _has(q, "code", "work", "line"):
        return (
            "Read the example top to bottom: each line does one thing. Run it, then change a value and predict the new "
            f"output before running again — that's the fastest way to really get {c}."
        )
    if _has(q, "mistake", "wrong", "avoid", "pitfall"):
        if ctx.key_points:
            return f"Most mistakes come from forgetting: {' · '.join(ctx.key_points[:2])}."
        return (
            f"The usual mistakes are using {c} where a simpler tool would do, and not testing the empty or edge case."
        )
    if _has(q, "when", "use", "why"):
        return f"Reach for {c} when it makes the job simpler or faster. {ctx.key_points[0] if ctx.key_points else ctx.explanation}"
    if _has(q, "complex", "big o", "fast", "slow"):
        return (
            f"Ask how many steps the operation takes as the input grows. For {c}, the lesson's key points show where "
            "it's fast — and where it isn't."
        )
    if _has(q, "next", "after", "learn"):
        return (
            f"Finish this lesson's quiz, then follow the next node on your course roadmap — it builds directly on {c}."
        )
    return f"Here's another angle on {c}: {ctx.analogy or ctx.explanation}"
