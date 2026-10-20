"""Typed function signatures inferred from a problem's test cases.

Typed languages (Java, C++, Go, Rust, …) need parameter and return types; the test data has JSON
values. Every argument position and the expected results are unified into one of a few types —
like LeetCode, which also sticks to ints, floats, bools, strings and (nested) lists of those.
A problem using anything else (objects, nulls, mixed lists) has no signature and is offered in
the dynamically typed languages only.
"""

import json
from dataclasses import dataclass
from typing import Any, Literal

ScalarKind = Literal["int", "long", "float", "bool", "string"]
INT32 = 2**31
INT64 = 2**63
MAX_LIST_DEPTH = 2


@dataclass(frozen=True)
class Type:
    kind: Literal["int", "long", "float", "bool", "string", "list", "unknown"]
    item: "Type | None" = None

    @property
    def depth(self) -> int:
        return 1 + self.item.depth if self.kind == "list" and self.item else 0

    @property
    def scalar(self) -> "Type":
        """The innermost element type."""
        return self.item.scalar if self.kind == "list" and self.item else self

    def __str__(self) -> str:
        return f"list[{self.item}]" if self.kind == "list" else self.kind


@dataclass(frozen=True)
class Param:
    name: str  # snake_case
    type: Type


@dataclass(frozen=True)
class Signature:
    params: tuple[Param, ...]
    returns: Type
    # Some cases expect an error (raise / throw / Err / error return).
    throws: bool


class Unsupported(ValueError):
    pass


UNKNOWN = Type("unknown")


def type_of(value: Any) -> Type:
    if isinstance(value, bool):
        return Type("bool")
    if isinstance(value, int):
        if abs(value) < INT32:
            return Type("int")
        if -INT64 <= value < INT64:
            return Type("long")
        raise Unsupported("integer too large for 64 bits")
    if isinstance(value, float):
        return Type("float")
    if isinstance(value, str):
        return Type("string")
    if isinstance(value, list):
        item = UNKNOWN
        for element in value:
            item = unify(item, type_of(element))
        return Type("list", item)
    raise Unsupported(f"unsupported value of type {type(value).__name__}")


def unify(a: Type, b: Type) -> Type:
    if a.kind == "unknown":
        return b
    if b.kind == "unknown":
        return a
    if a == b:
        return a
    numeric = {"int": 0, "long": 1, "float": 2}
    if a.kind in numeric and b.kind in numeric:
        return a if numeric[a.kind] > numeric[b.kind] else b
    if a.kind == "list" and b.kind == "list":
        return Type("list", unify(a.item or UNKNOWN, b.item or UNKNOWN))
    raise Unsupported(f"mixes {a} and {b}")


def _resolve(t: Type) -> Type:
    """An element type nobody could observe (every list empty) defaults to int."""
    if t.kind == "unknown":
        return Type("int")
    if t.kind == "list":
        return Type("list", _resolve(t.item or UNKNOWN))
    return t


def infer_signature(
    param_names: list[str], case_args: list[list[Any]], expected: list[Any | None], *, throws: bool
) -> Signature:
    """`expected[i]` is the decoded expected value of case i, or None for an error case."""
    if not case_args:
        raise Unsupported("no test cases")
    if any(len(args) != len(param_names) for args in case_args):
        raise Unsupported("argument count differs from the parameter list")
    types = [UNKNOWN] * len(param_names)
    for args in case_args:
        types = [unify(t, type_of(a)) for t, a in zip(types, args, strict=True)]
    returns = UNKNOWN
    values = [e for e in expected if e is not None]
    if not values:
        raise Unsupported("no case returns a value")
    for value in values:
        returns = unify(returns, type_of(value))
    resolved = [_resolve(t) for t in (*types, returns)]
    if any(t.depth > MAX_LIST_DEPTH for t in resolved):
        raise Unsupported("lists nested too deeply")
    return Signature(
        params=tuple(Param(n, t) for n, t in zip(param_names, resolved[:-1], strict=True)),
        returns=resolved[-1],
        throws=throws,
    )


def signature_for(param_names: list[str], cases: list[Any]) -> Signature:
    """From test cases with `.input` (call arguments as JSON) and `.expected_output` / `.expected_error`."""
    args = [json.loads(f"[{c.input}]") for c in cases]
    expected = [None if c.expected_error is not None else json.loads(c.expected_output) for c in cases]
    return infer_signature(param_names, args, expected, throws=any(c.expected_error is not None for c in cases))
