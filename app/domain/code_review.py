"""Static, heuristic review of a passing solution: complexity estimate and a code-quality score.

It reads loop nesting, recursion, sorting and auxiliary collections from the source. It's an
estimate shown to motivate learners, not a proof — swap in a model-backed reviewer later.
"""

import re

from app.schemas.practice import AiReview

_PY_LOOP = re.compile(r"^\s*(for|while)\b")
_JS_LOOP = re.compile(r"\b(for|while)\s*\(|\.(forEach|map|filter|reduce|some|every|find|findIndex)\s*\(")
_SORT = re.compile(r"\bsorted\s*\(|\.sort\s*\(")
_AUX_PY = re.compile(r"\{\}|\bdict\s*\(|\bset\s*\(|\[\]|\blist\s*\(|defaultdict|Counter|\.append\(")
_AUX_JS = re.compile(r"new\s+(Map|Set|Array)\b|\[\]|\{\}|\.push\(")
_ALLOWED_SHORT = {"i", "j", "k", "n", "m", "x", "y", "_", "l", "r"}


def _python_depth(lines: list[str]) -> int:
    stack: list[int] = []
    deepest = 0
    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        while stack and indent <= stack[-1]:
            stack.pop()
        if _PY_LOOP.match(line):
            stack.append(indent)
            deepest = max(deepest, len(stack))
    return deepest


def _js_depth(code: str) -> int:
    depth_at_loop: list[int] = []
    brace = 0
    deepest = 0
    for line in code.splitlines():
        if _JS_LOOP.search(line):
            while depth_at_loop and brace <= depth_at_loop[-1]:
                depth_at_loop.pop()
            depth_at_loop.append(brace)
            deepest = max(deepest, len(depth_at_loop))
        brace += line.count("{") - line.count("}")
        while depth_at_loop and brace <= depth_at_loop[-1]:
            depth_at_loop.pop()
    return deepest


def _is_recursive(code: str, entry: str) -> bool:
    return len(re.findall(rf"\b{re.escape(entry)}\s*\(", code)) > 1


def review(code: str, language: str, entry: str) -> AiReview:
    lines = code.splitlines()
    depth = _python_depth(lines) if language == "python" else _js_depth(code)
    recursive = _is_recursive(code, entry)
    sorts = bool(_SORT.search(code))
    aux = bool((_AUX_PY if language == "python" else _AUX_JS).search(code))

    if recursive and depth == 0:
        time = "O(2ⁿ) or O(n) with memoization"
    elif depth >= 2:
        time = f"O(n^{depth})" if depth > 2 else "O(n²)"
    elif sorts:
        time = "O(n log n)"
    elif depth == 1:
        time = "O(n)"
    else:
        time = "O(1) / O(log n)"
    space = "O(n)" if aux or recursive else "O(1)"

    quality = 100
    notes: list[str] = []
    long_lines = sum(1 for line in lines if len(line) > 100)
    if long_lines:
        quality -= min(15, 5 * long_lines)
        notes.append("break up lines longer than 100 characters")
    names = set(re.findall(r"\b(?:let|const|var)\s+([A-Za-z_]\w*)|^\s*([A-Za-z_]\w*)\s*=(?!=)", code, re.M))
    short = {n for pair in names for n in pair if n and len(n) == 1 and n not in _ALLOWED_SHORT}
    if short:
        quality -= min(15, 5 * len(short))
        notes.append(f"give {', '.join(sorted(short))} more descriptive names")
    if re.search(r"\b(TODO|FIXME)\b", code):
        quality -= 5
        notes.append("resolve leftover TODOs")
    if re.search(r"^\s*print\(|console\.log\(", code, re.M):
        quality -= 5
        notes.append("remove debug prints before submitting")
    if depth >= 2:
        quality -= 10
    quality = max(40, quality)

    if depth >= 2:
        recommendation = "It works, but nested loops make it quadratic. A hash map or two pointers can usually bring this down to O(n)."
    elif recursive and depth == 0:
        recommendation = (
            "Recursive and correct. Cache results you compute more than once (memoization) to avoid exponential time."
        )
    elif notes:
        recommendation = f"Solid solution at {time}. To polish it: {'; '.join(notes)}."
    else:
        recommendation = f"Clean solution at {time} time and {space} space. Nicely done."

    return AiReview(
        correct=True, time_complexity=time, space_complexity=space, code_quality=quality, recommendation=recommendation
    )
