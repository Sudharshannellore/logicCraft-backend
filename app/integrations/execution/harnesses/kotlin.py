"""Kotlin: `class Solution` with IntArray/Array<String>/…, like LeetCode. main.kt (harness) + solution.kt."""

from typing import Any

from app.domain.signatures import Signature, Type
from app.integrations.execution.harnesses.base import MARKER, Program, TypedHarness, camel, escape_string

_SCALARS = {"int": "Int", "long": "Long", "float": "Double", "bool": "Boolean", "string": "String"}
_PRIMITIVE_ARRAYS = {"int": "IntArray", "long": "LongArray", "float": "DoubleArray", "bool": "BooleanArray"}
_ARRAY_OF = {"int": "intArrayOf", "long": "longArrayOf", "float": "doubleArrayOf", "bool": "booleanArrayOf"}
_DEFAULTS = {"int": "0", "long": "0L", "float": "0.0", "bool": "false", "string": '""'}

_MAIN = """fun lcQ(s: String): String {
    val b = StringBuilder("\\"")
    for (c in s) {
        when {
            c == '"' -> b.append("\\\\\\"")
            c == '\\\\' -> b.append("\\\\\\\\")
            c.code < 0x20 || c.code > 0x7e -> b.append("\\\\u%04x".format(c.code))
            else -> b.append(c)
        }
    }
    return b.append('"').toString()
}

fun lcJson(v: Any?): String = when (v) {
    null -> "null"
    is String -> lcQ(v)
    is Char -> lcQ(v.toString())
    is Boolean, is Int, is Long, is Double -> v.toString()
    is IntArray -> v.joinToString(",", "[", "]")
    is LongArray -> v.joinToString(",", "[", "]")
    is DoubleArray -> v.joinToString(",", "[", "]")
    is BooleanArray -> v.joinToString(",", "[", "]")
    is Array<*> -> v.joinToString(",", "[", "]") { lcJson(it) }
    is Iterable<*> -> v.joinToString(",", "[", "]") { lcJson(it) }
    else -> lcQ(v.toString())
}

fun lcEmit(run: () -> Any?) {
    val line = try {
        "{\\"ok\\":true,\\"value\\":" + lcJson(run()) + "}"
    } catch (t: Throwable) {
        "{\\"ok\\":false,\\"error\\":" + lcQ(t.javaClass.simpleName + (t.message?.let { ": " + it } ?: "")) + "}"
    }
    println(line)
    System.out.flush()
}

fun main() {
    println()
    println("__MARKER__")
__CASES__
}
""".replace("__MARKER__", MARKER)


class KotlinHarness(TypedHarness):
    language = "kotlin"
    label = "Kotlin"

    def entrypoint(self, snake: str) -> str:
        return camel(snake)

    def type_name(self, t: Type) -> str:
        if t.kind == "list":
            item = t.item
            return _PRIMITIVE_ARRAYS[item.kind] if item.kind in _PRIMITIVE_ARRAYS else f"Array<{self.type_name(item)}>"
        return _SCALARS[t.kind]

    def literal(self, value: Any, t: Type) -> str:
        if t.kind == "list":
            item = t.item
            elements = ", ".join(self.literal(v, item) for v in value)
            if item.kind in _ARRAY_OF:
                return f"{_ARRAY_OF[item.kind]}({elements})"
            return f"arrayOf<{self.type_name(item)}>({elements})"
        if t.kind == "string":
            return f'"{escape_string(value, unicode="\\u{:04x}", surrogates=True, extra={"$": "\\$"})}"'
        if t.kind == "long":
            return f"{int(value)}L"
        return self.scalar_literal(value, t)

    def _default(self, t: Type) -> str:
        if t.kind == "list":
            return f"{_ARRAY_OF[t.item.kind]}()" if t.item.kind in _ARRAY_OF else f"arrayOf<{self.type_name(t.item)}>()"
        return _DEFAULTS[t.kind]

    def starter(self, entry: str, signature: Signature | None, param_names: list[str]) -> str:
        assert signature
        params = ", ".join(f"{camel(p.name)}: {self.type_name(p.type)}" for p in signature.params)
        hint = (
            '        // Invalid input: throw IllegalArgumentException("message the tests expect")\n'
            if signature.throws
            else ""
        )
        return (
            "class Solution {\n"
            f"    fun {entry}({params}): {self.type_name(signature.returns)} {{\n"
            f"{hint}        // Write your solution here\n"
            f"        return {self._default(signature.returns)}\n"
            "    }\n}\n"
        )

    def build(self, code: str, entry: str, signature: Signature | None, case_args: list[list[Any]]) -> Program:
        assert signature
        cases = "\n".join(
            f"    lcEmit {{ Solution().{entry}("
            + ", ".join(self.literal(a, p.type) for a, p in zip(args, signature.params, strict=True))
            + ") }"
            for args in case_args
        )
        return Program(
            files={"main.kt": _MAIN.replace("__CASES__", cases), "solution.kt": code}, solution="solution.kt"
        )
