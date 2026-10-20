"""Go: a top-level function in package main, like LeetCode. Error cases use Go's idiom — the function
returns (T, error). main.go (harness, uses encoding/json) + solution.go, built together.
"""

from typing import Any

from app.domain.signatures import Signature, Type
from app.integrations.execution.harnesses.base import MARKER, Program, TypedHarness, camel, escape_string

_SCALARS = {"int": "int", "long": "int", "float": "float64", "bool": "bool", "string": "string"}
_DEFAULTS = {"int": "0", "long": "0", "float": "0", "bool": "false", "string": '""'}

_MAIN = """package main

import (
\t"encoding/json"
\t"fmt"
\t"os"
)

func lcEmit(run func() (any, error)) {
\tvar line []byte
\tfunc() {
\t\tdefer func() {
\t\t\tif r := recover(); r != nil {
\t\t\t\tline, _ = json.Marshal(map[string]any{"ok": false, "error": fmt.Sprint(r)})
\t\t\t}
\t\t}()
\t\tv, err := run()
\t\tif err != nil {
\t\t\tline, _ = json.Marshal(map[string]any{"ok": false, "error": err.Error()})
\t\t\treturn
\t\t}
\t\tif encoded, e := json.Marshal(map[string]any{"ok": true, "value": v}); e == nil {
\t\t\tline = encoded
\t\t} else {
\t\t\tline, _ = json.Marshal(map[string]any{"ok": false, "error": "result can't be encoded: " + e.Error()})
\t\t}
\t}()
\tos.Stdout.Write(append(line, '\\n'))
}

func main() {
\tfmt.Println()
\tfmt.Println("__MARKER__")
__CASES__
}
""".replace("__MARKER__", MARKER)


class GoHarness(TypedHarness):
    language = "go"
    label = "Go"

    def entrypoint(self, snake: str) -> str:
        return camel(snake)

    def type_name(self, t: Type) -> str:
        return f"[]{self.type_name(t.item)}" if t.kind == "list" else _SCALARS[t.kind]

    def literal(self, value: Any, t: Type) -> str:
        if t.kind == "list":
            return f"{self.type_name(t)}{{{', '.join(self.literal(v, t.item) for v in value)}}}"
        if t.kind == "string":
            return f'"{escape_string(value, unicode="\\U{:08x}")}"'
        return self.scalar_literal(value, t)

    def starter(self, entry: str, signature: Signature | None, param_names: list[str]) -> str:
        assert signature
        params = ", ".join(f"{camel(p.name)} {self.type_name(p.type)}" for p in signature.params)
        returns = signature.returns
        zero = "nil" if returns.kind == "list" else _DEFAULTS[returns.kind]
        if signature.throws:
            return (
                "package main\n\n"
                "// For invalid input, return an error with the message the tests expect:\n"
                '//   return <zero value>, errors.New("message")   (and add: import "errors")\n'
                f"func {entry}({params}) ({self.type_name(returns)}, error) {{\n"
                f"\t// Write your solution here\n\treturn {zero}, nil\n}}\n"
            )
        return (
            "package main\n\n"
            f"func {entry}({params}) {self.type_name(returns)} {{\n"
            f"\t// Write your solution here\n\treturn {zero}\n}}\n"
        )

    def build(self, code: str, entry: str, signature: Signature | None, case_args: list[list[Any]]) -> Program:
        assert signature
        returns = signature.returns
        # A nil slice would encode as null; the tests expect [].
        fix_nil = f"if v == nil {{ v = {self.type_name(returns)}{{}} }}; " if returns.kind == "list" else ""
        lines = []
        for args in case_args:
            call = f"{entry}({', '.join(self.literal(a, p.type) for a, p in zip(args, signature.params, strict=True))})"
            if signature.throws:
                body = f"v, err := {call}; if err != nil {{ return nil, err }}; {fix_nil}return v, nil"
            else:
                body = f"v := {call}; {fix_nil}return v, nil"
            lines.append(f"\tlcEmit(func() (any, error) {{ {body} }})")
        return Program(
            files={"main.go": _MAIN.replace("__CASES__", "\n".join(lines)), "solution.go": code}, solution="solution.go"
        )
