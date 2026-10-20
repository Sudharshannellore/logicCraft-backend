"""C: LeetCode's conventions — arrays come with a size (`int* nums, int numsSize`) and returned arrays
report theirs through `int* returnSize`. No exceptions in C, so problems with error cases (and
nested lists) aren't offered in C. main.c #includes solution.c.
"""

from typing import Any

from app.domain.signatures import Signature, Type
from app.integrations.execution.harnesses.base import MARKER, Program, TypedHarness, camel, escape_string

_SCALARS = {"int": "int", "long": "long long", "float": "double", "bool": "bool", "string": "char*"}
_DEFAULTS = {"int": "0", "long": "0", "float": "0.0", "bool": "false", "string": '""'}
_PRINTERS = {"int": "lc_int", "long": "lc_long", "float": "lc_double", "bool": "lc_bool", "string": "lc_str"}

_MAIN = """#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "solution.c"

static void lc_str(const char* s) {
    if (!s) { fputs("null", stdout); return; }
    putchar('"');
    for (const unsigned char* p = (const unsigned char*)s; *p; p++) {
        if (*p == '"') fputs("\\\\\\"", stdout);
        else if (*p == '\\\\') fputs("\\\\\\\\", stdout);
        else if (*p < 0x20 || *p == 0x7f) printf("\\\\u%04x", *p);
        else putchar(*p);
    }
    putchar('"');
}
static void lc_int(int v) { printf("%d", v); }
static void lc_long(long long v) { printf("%lld", v); }
static void lc_double(double v) { printf("%.17g", v); }
static void lc_bool(bool v) { fputs(v ? "true" : "false", stdout); }
static void lc_open(void) { fputs("{\\"ok\\":true,\\"value\\":", stdout); }
static void lc_close(void) { fputs("}\\n", stdout); fflush(stdout); }

int main(void) {
    printf("\\n__MARKER__\\n");
    fflush(stdout);
__CASES__
    return 0;
}
""".replace("__MARKER__", MARKER)


class CHarness(TypedHarness):
    language = "c"
    label = "C"

    def entrypoint(self, snake: str) -> str:
        return snake

    def supports(self, signature: Signature | None) -> bool:
        if signature is None or signature.throws:
            return False
        return all(t.depth <= 1 for t in (*(p.type for p in signature.params), signature.returns))

    def type_name(self, t: Type) -> str:
        return f"{_SCALARS[t.item.kind]}*" if t.kind == "list" else _SCALARS[t.kind]

    def literal(self, value: Any, t: Type) -> str:
        if t.kind == "string":
            return f'"{escape_string(value, unicode="raw")}"'
        if t.kind == "long":
            return f"{int(value)}LL"
        return self.scalar_literal(value, t)

    def _params(self, signature: Signature) -> list[str]:
        out = []
        for p in signature.params:
            name = camel(p.name)
            if p.type.kind == "list":
                out += [f"{self.type_name(p.type)} {name}", f"int {name}Size"]
            else:
                out.append(f"{self.type_name(p.type)} {name}")
        if signature.returns.kind == "list":
            out.append("int* returnSize")
        return out

    def starter(self, entry: str, signature: Signature | None, param_names: list[str]) -> str:
        assert signature
        returns = signature.returns
        if returns.kind == "list":
            body = (
                "    // Return a malloc'd array and set *returnSize to its length.\n"
                "    *returnSize = 0;\n"
                "    return NULL;\n"
            )
        else:
            body = f"    // Write your solution here\n    return {_DEFAULTS[returns.kind]};\n"
        return (
            "#include <stdbool.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
            f"{self.type_name(returns)} {entry}({', '.join(self._params(signature))}) {{\n{body}}}\n"
        )

    def build(self, code: str, entry: str, signature: Signature | None, case_args: list[list[Any]]) -> Program:
        assert signature
        returns = signature.returns
        blocks = []
        for args in case_args:
            decls, call = [], []
            for i, (value, p) in enumerate(zip(args, signature.params, strict=True)):
                if p.type.kind == "list":
                    item = p.type.item
                    elements = ", ".join(self.literal(v, item) for v in value) or self.literal(
                        "" if item.kind == "string" else 0, item
                    )
                    decls.append(f"{_SCALARS[item.kind]} a{i}[] = {{{elements}}};")
                    call += [f"a{i}", str(len(value))]
                elif p.type.kind == "string":
                    decls.append(f"char a{i}[] = {self.literal(value, p.type)};")  # a writable copy
                    call.append(f"a{i}")
                else:
                    call.append(self.literal(value, p.type))
            if returns.kind == "list":
                printer = _PRINTERS[returns.item.kind]
                emit = (
                    f"int rs = 0; {self.type_name(returns)} r = {entry}({', '.join([*call, '&rs'])}); lc_open(); "
                    f"putchar('['); for (int k = 0; k < rs; k++) {{ if (k) putchar(','); {printer}(r[k]); }} putchar(']'); lc_close();"
                )
            else:
                emit = f"{self.type_name(returns)} r = {entry}({', '.join(call)}); lc_open(); {_PRINTERS[returns.kind]}(r); lc_close();"
            blocks.append(f"    {{ {' '.join(decls)} {emit} }}")
        return Program(
            files={"main.c": _MAIN.replace("__CASES__", "\n".join(blocks)), "solution.c": code}, solution="solution.c"
        )
