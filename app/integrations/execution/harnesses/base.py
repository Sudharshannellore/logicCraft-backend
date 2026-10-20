"""What every language's harness provides, and the helpers they share.

A harness turns (learner code, entry function, signature, test arguments) into a runnable program
whose output is: the learner's own prints, then the marker line, then one JSON object per test —
{"ok": true, "value": …} or {"ok": false, "error": "…"}. One line per test means a crash on test 5
still reports tests 1–4.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.domain.signatures import Signature, Type

MARKER = "__LOGICRAFT_RESULTS__"


@dataclass(frozen=True)
class Program:
    """Source files to write into the run folder. `solution` is the file holding the learner's code."""

    files: dict[str, str]
    solution: str


def camel(snake: str) -> str:
    head, *rest = snake.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in rest)


def pascal(snake: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in snake.split("_"))


def escape_string(s: str, *, unicode: str, surrogates: bool = False, extra: dict[str, str] | None = None) -> str:
    """Body of a double-quoted string literal in a C-family language.

    `unicode` formats a code point: "\\u{:04x}" (Java, C#, Kotlin — with `surrogates`, as their strings
    are UTF-16), "\\U{:08x}" (Go), "\\u{{{:x}}}" (Rust, Swift, PHP), or "raw" (C, C++: non-ASCII stays
    as UTF-8 and control characters become fixed-width octal, which can't swallow a following digit).
    """
    named = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t", **(extra or {})}
    out = []
    for ch in s:
        code = ord(ch)
        if ch in named:
            out.append(named[ch])
        elif code < 0x20 or code == 0x7F:
            out.append(f"\\{code:03o}" if unicode == "raw" else unicode.format(code))
        elif code > 0x7F and unicode != "raw":
            if code > 0xFFFF and surrogates:
                code -= 0x10000
                out.append(unicode.format(0xD800 + (code >> 10)) + unicode.format(0xDC00 + (code & 0x3FF)))
            else:
                out.append(unicode.format(code))
        else:
            out.append(ch)
    return "".join(out)


def float_literal(value: float) -> str:
    text = repr(float(value))
    return text if any(c in text for c in ".eEn") else text + ".0"


class Harness(ABC):
    language: str
    label: str
    # Works without a typed signature (dynamically typed languages).
    dynamic: bool = False

    @abstractmethod
    def entrypoint(self, snake: str) -> str: ...

    def supports(self, signature: Signature | None) -> bool:
        return self.dynamic or signature is not None

    @abstractmethod
    def starter(self, entry: str, signature: Signature | None, param_names: list[str]) -> str: ...

    @abstractmethod
    def build(self, code: str, entry: str, signature: Signature | None, case_args: list[list[Any]]) -> Program: ...


class TypedHarness(Harness):
    """Typed languages: each test's arguments become source literals of the parameter types."""

    @abstractmethod
    def type_name(self, t: Type) -> str: ...

    @abstractmethod
    def literal(self, value: Any, t: Type) -> str: ...

    def scalar_literal(self, value: Any, t: Type) -> str:
        if t.kind == "bool":
            return "true" if value else "false"
        if t.kind == "float":
            return float_literal(value)
        return str(int(value))
