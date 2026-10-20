"""C++: `class Solution` taking `vector<int>& nums`, like LeetCode. main.cpp #includes solution.cpp."""

from typing import Any

from app.domain.signatures import Signature, Type
from app.integrations.execution.harnesses.base import MARKER, Program, TypedHarness, camel, escape_string

_SCALARS = {"int": "int", "long": "long long", "float": "double", "bool": "bool", "string": "string"}
_DEFAULTS = {"int": "0", "long": "0", "float": "0.0", "bool": "false", "string": '""'}

_MAIN = """#include <cstdio>
#include <exception>
#include <iostream>
#include <string>
#include <vector>
#include "solution.cpp"

static std::string lc_q(const std::string& s) {
    std::string out = "\\"";
    for (unsigned char c : s) {
        if (c == '"') out += "\\\\\\"";
        else if (c == '\\\\') out += "\\\\\\\\";
        else if (c < 0x20 || c == 0x7f) { char buf[8]; std::snprintf(buf, sizeof buf, "\\\\u%04x", c); out += buf; }
        else out += static_cast<char>(c);
    }
    return out + "\\"";
}
static std::string lc_json(int v) { return std::to_string(v); }
static std::string lc_json(long long v) { return std::to_string(v); }
static std::string lc_json(long v) { return std::to_string(v); }
static std::string lc_json(double v) { char buf[32]; std::snprintf(buf, sizeof buf, "%.17g", v); return buf; }
static std::string lc_json(bool v) { return v ? "true" : "false"; }
static std::string lc_json(const std::string& v) { return lc_q(v); }
static std::string lc_json(const char* v) { return v ? lc_q(v) : "null"; }
template <class T> static std::string lc_json(const std::vector<T>& v) {
    std::string out = "[";
    for (size_t i = 0; i < v.size(); i++) { if (i) out += ","; out += lc_json(static_cast<T>(v[i])); }
    return out + "]";
}
template <class F> static void lc_emit(F run) {
    std::string line;
    try { line = "{\\"ok\\":true,\\"value\\":" + lc_json(run()) + "}"; }
    catch (const std::exception& e) { line = "{\\"ok\\":false,\\"error\\":" + lc_q(e.what()) + "}"; }
    catch (...) { line = "{\\"ok\\":false,\\"error\\":\\"unknown exception\\"}"; }
    std::cout << line << std::endl;
}

int main() {
    std::cout << "\\n__MARKER__" << std::endl;
__CASES__
    return 0;
}
""".replace("__MARKER__", MARKER)


class CppHarness(TypedHarness):
    language = "cpp"
    label = "C++"

    def entrypoint(self, snake: str) -> str:
        return camel(snake)

    def type_name(self, t: Type) -> str:
        return f"vector<{self.type_name(t.item)}>" if t.kind == "list" else _SCALARS[t.kind]

    def _std(self, t: Type) -> str:
        """Fully qualified, for the harness (which doesn't assume `using namespace std`)."""
        if t.kind == "list":
            return f"std::vector<{self._std(t.item)}>"
        return "std::string" if t.kind == "string" else _SCALARS[t.kind]

    def literal(self, value: Any, t: Type) -> str:
        if t.kind == "list":
            return f"{self._std(t)}{{{', '.join(self.literal(v, t.item) for v in value)}}}"
        if t.kind == "string":
            return f'std::string("{escape_string(value, unicode="raw")}")'
        if t.kind == "long":
            return f"{int(value)}LL"
        return self.scalar_literal(value, t)

    def _param(self, name: str, t: Type) -> str:
        return f"{self.type_name(t)}& {name}" if t.kind == "list" else f"{self.type_name(t)} {name}"

    def starter(self, entry: str, signature: Signature | None, param_names: list[str]) -> str:
        assert signature
        params = ", ".join(self._param(camel(p.name), p.type) for p in signature.params)
        returns = signature.returns
        default = "{}" if returns.kind == "list" else _DEFAULTS[returns.kind]
        hint = (
            '        // Invalid input: throw invalid_argument("message the tests expect");\n'
            if signature.throws
            else ""
        )
        return (
            "#include <bits/stdc++.h>\nusing namespace std;\n\n"
            "class Solution {\npublic:\n"
            f"    {self.type_name(returns)} {entry}({params}) {{\n"
            f"{hint}        // Write your solution here\n"
            f"        return {default};\n"
            "    }\n};\n"
        )

    def build(self, code: str, entry: str, signature: Signature | None, case_args: list[list[Any]]) -> Program:
        assert signature
        blocks = []
        for args in case_args:
            # Named locals, so `vector<int>& nums` parameters can bind to them.
            decls = " ".join(
                f"auto lc_a{i} = {self.literal(a, p.type)};"
                for i, (a, p) in enumerate(zip(args, signature.params, strict=True))
            )
            call = ", ".join(f"lc_a{i}" for i in range(len(args)))
            blocks.append(f"    {{ {decls} lc_emit([&]() {{ return Solution().{entry}({call}); }}); }}")
        return Program(
            files={"main.cpp": _MAIN.replace("__CASES__", "\n".join(blocks)), "solution.cpp": code},
            solution="solution.cpp",
        )
