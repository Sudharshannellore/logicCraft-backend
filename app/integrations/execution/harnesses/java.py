"""Java: `class Solution` with an instance method, like LeetCode. Main.java (harness) + Solution.java."""

from typing import Any

from app.domain.signatures import Signature, Type
from app.integrations.execution.harnesses.base import MARKER, Program, TypedHarness, camel, escape_string

_SCALARS = {"int": "int", "long": "long", "float": "double", "bool": "boolean", "string": "String"}
_DEFAULTS = {"int": "0", "long": "0L", "float": "0.0", "bool": "false", "string": '""'}

_MAIN = """import java.util.*;

public class Main {
    static String lcQ(String s) {
        StringBuilder b = new StringBuilder("\\"");
        for (char c : s.toCharArray()) {
            if (c == '"') b.append("\\\\\\"");
            else if (c == '\\\\') b.append("\\\\\\\\");
            else if (c < 0x20 || c > 0x7e) b.append(String.format("\\\\u%04x", (int) c));
            else b.append(c);
        }
        return b.append('"').toString();
    }

    static String lcJson(Object v) {
        if (v == null) return "null";
        if (v instanceof String s) return lcQ(s);
        if (v instanceof Character c) return lcQ(String.valueOf(c));
        if (v instanceof Boolean || v instanceof Integer || v instanceof Long || v instanceof Double) return v.toString();
        if (v instanceof int[] a) { StringJoiner j = new StringJoiner(",", "[", "]"); for (int x : a) j.add(String.valueOf(x)); return j.toString(); }
        if (v instanceof long[] a) { StringJoiner j = new StringJoiner(",", "[", "]"); for (long x : a) j.add(String.valueOf(x)); return j.toString(); }
        if (v instanceof double[] a) { StringJoiner j = new StringJoiner(",", "[", "]"); for (double x : a) j.add(String.valueOf(x)); return j.toString(); }
        if (v instanceof boolean[] a) { StringJoiner j = new StringJoiner(",", "[", "]"); for (boolean x : a) j.add(String.valueOf(x)); return j.toString(); }
        if (v instanceof Object[] a) { StringJoiner j = new StringJoiner(",", "[", "]"); for (Object x : a) j.add(lcJson(x)); return j.toString(); }
        if (v instanceof Iterable<?> it) { StringJoiner j = new StringJoiner(",", "[", "]"); for (Object x : it) j.add(lcJson(x)); return j.toString(); }
        return lcQ(v.toString());
    }

    interface LcCase { Object run() throws Throwable; }

    static void lcEmit(LcCase c) {
        String line;
        try {
            line = "{\\"ok\\":true,\\"value\\":" + lcJson(c.run()) + "}";
        } catch (Throwable t) {
            String msg = t.getMessage();
            line = "{\\"ok\\":false,\\"error\\":" + lcQ(t.getClass().getSimpleName() + (msg == null ? "" : ": " + msg)) + "}";
        }
        System.out.println(line);
        System.out.flush();
    }

    public static void main(String[] args) {
        System.out.println();
        System.out.println("__MARKER__");
__CASES__
    }
}
""".replace("__MARKER__", MARKER)


class JavaHarness(TypedHarness):
    language = "java"
    label = "Java"

    def entrypoint(self, snake: str) -> str:
        return camel(snake)

    def type_name(self, t: Type) -> str:
        return f"{self.type_name(t.item)}[]" if t.kind == "list" else _SCALARS[t.kind]

    def literal(self, value: Any, t: Type) -> str:
        if t.kind == "list":
            return f"new {self.type_name(t)}{{{', '.join(self.literal(v, t.item) for v in value)}}}"
        if t.kind == "string":
            return f'"{escape_string(value, unicode="\\u{:04x}", surrogates=True)}"'
        if t.kind == "long":
            return f"{int(value)}L"
        return self.scalar_literal(value, t)

    def starter(self, entry: str, signature: Signature | None, param_names: list[str]) -> str:
        assert signature
        params = ", ".join(f"{self.type_name(p.type)} {camel(p.name)}" for p in signature.params)
        default = (
            f"new {self.type_name(signature.returns.item)}[0]"
            if signature.returns.kind == "list"
            else _DEFAULTS[signature.returns.kind]
        )
        hint = (
            '        // Invalid input: throw new IllegalArgumentException("message the tests expect");\n'
            if signature.throws
            else ""
        )
        return (
            "import java.util.*;\n\n"
            "class Solution {\n"
            f"    public {self.type_name(signature.returns)} {entry}({params}) {{\n"
            f"{hint}        // Write your solution here\n"
            f"        return {default};\n"
            "    }\n"
            "}\n"
        )

    def build(self, code: str, entry: str, signature: Signature | None, case_args: list[list[Any]]) -> Program:
        assert signature
        cases = "\n".join(
            "        lcEmit(() -> new Solution()."
            + f"{entry}({', '.join(self.literal(a, p.type) for a, p in zip(args, signature.params, strict=True))}));"
            for args in case_args
        )
        return Program(
            files={"Main.java": _MAIN.replace("__CASES__", cases), "Solution.java": code}, solution="Solution.java"
        )
