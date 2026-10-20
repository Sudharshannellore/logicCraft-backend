"""Rust: `impl Solution { pub fn … }` with a `struct Solution;` the harness provides, like LeetCode.
Error cases return Result<T, String>. main.rs include!s solution.rs; panics are caught per test.
"""

from typing import Any

from app.domain.signatures import Signature, Type
from app.integrations.execution.harnesses.base import MARKER, Program, TypedHarness, escape_string, float_literal

_SCALARS = {"int": "i32", "long": "i64", "float": "f64", "bool": "bool", "string": "String"}
_DEFAULTS = {"int": "0", "long": "0", "float": "0.0", "bool": "false", "string": "String::new()"}

_MAIN = """#![allow(dead_code, unused_imports, unused_variables, unused_mut, non_snake_case)]

pub struct Solution;

include!("solution.rs");

fn lc_q(s: &str) -> String {
    let mut out = String::from("\\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\\\\""),
            '\\\\' => out.push_str("\\\\\\\\"),
            c if (c as u32) < 0x20 || c as u32 == 0x7f => out.push_str(&format!("\\\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

trait LcJson { fn lc_json(&self) -> String; }
impl LcJson for i32 { fn lc_json(&self) -> String { self.to_string() } }
impl LcJson for i64 { fn lc_json(&self) -> String { self.to_string() } }
impl LcJson for usize { fn lc_json(&self) -> String { self.to_string() } }
impl LcJson for f64 { fn lc_json(&self) -> String { format!("{:?}", self) } }
impl LcJson for bool { fn lc_json(&self) -> String { self.to_string() } }
impl LcJson for String { fn lc_json(&self) -> String { lc_q(self) } }
impl LcJson for &str { fn lc_json(&self) -> String { lc_q(self) } }
impl<T: LcJson> LcJson for Vec<T> {
    fn lc_json(&self) -> String { format!("[{}]", self.iter().map(|x| x.lc_json()).collect::<Vec<_>>().join(",")) }
}

fn lc_panic_message(e: Box<dyn std::any::Any + Send>) -> String {
    if let Some(s) = e.downcast_ref::<&str>() { s.to_string() }
    else if let Some(s) = e.downcast_ref::<String>() { s.clone() }
    else { "panicked".to_string() }
}

fn lc_ok(value: String) { println!("{{\\"ok\\":true,\\"value\\":{}}}", value); }
fn lc_err(message: String) { println!("{{\\"ok\\":false,\\"error\\":{}}}", lc_q(&message)); }

fn main() {
    std::panic::set_hook(Box::new(|_| {}));
    println!();
    println!("__MARKER__");
__CASES__
}
""".replace("__MARKER__", MARKER)


class RustHarness(TypedHarness):
    language = "rust"
    label = "Rust"

    def entrypoint(self, snake: str) -> str:
        return snake

    def type_name(self, t: Type) -> str:
        return f"Vec<{self.type_name(t.item)}>" if t.kind == "list" else _SCALARS[t.kind]

    def literal(self, value: Any, t: Type) -> str:
        if t.kind == "list":
            if not value:
                return f"Vec::<{self.type_name(t.item)}>::new()"
            return f"vec![{', '.join(self.literal(v, t.item) for v in value)}]"
        if t.kind == "string":
            return f'String::from("{escape_string(value, unicode="\\u{{{:x}}}")}")'
        if t.kind == "float":
            return float_literal(value)
        if t.kind in ("int", "long"):
            return f"{int(value)}{_SCALARS[t.kind]}"
        return self.scalar_literal(value, t)

    def starter(self, entry: str, signature: Signature | None, param_names: list[str]) -> str:
        assert signature
        params = ", ".join(f"{p.name}: {self.type_name(p.type)}" for p in signature.params)
        returns = signature.returns
        zero = "vec![]" if returns.kind == "list" else _DEFAULTS[returns.kind]
        if signature.throws:
            ret, body = f"Result<{self.type_name(returns)}, String>", f"Ok({zero})"
            hint = '        // Invalid input: return Err("message the tests expect".to_string());\n'
        else:
            ret, body, hint = self.type_name(returns), zero, ""
        return (
            "impl Solution {\n"
            f"    pub fn {entry}({params}) -> {ret} {{\n"
            f"{hint}        // Write your solution here\n"
            f"        {body}\n"
            "    }\n}\n"
        )

    def build(self, code: str, entry: str, signature: Signature | None, case_args: list[list[Any]]) -> Program:
        assert signature
        lines = []
        for args in case_args:
            call = f"Solution::{entry}({', '.join(self.literal(a, p.type) for a, p in zip(args, signature.params, strict=True))})"
            if signature.throws:
                handle = (
                    "Ok(Ok(v)) => lc_ok(v.lc_json()), Ok(Err(e)) => lc_err(e), Err(p) => lc_err(lc_panic_message(p))"
                )
            else:
                handle = "Ok(v) => lc_ok(v.lc_json()), Err(p) => lc_err(lc_panic_message(p))"
            lines.append(f"    match std::panic::catch_unwind(|| {call}) {{ {handle} }}")
        return Program(
            files={"main.rs": _MAIN.replace("__CASES__", "\n".join(lines)), "solution.rs": code}, solution="solution.rs"
        )
