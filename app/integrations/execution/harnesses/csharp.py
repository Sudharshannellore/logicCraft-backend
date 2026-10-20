"""C#: `public class Solution` with PascalCase methods, like LeetCode. Program.cs (harness) + Solution.cs."""

from typing import Any

from app.domain.signatures import Signature, Type
from app.integrations.execution.harnesses.base import MARKER, Program, TypedHarness, camel, escape_string, pascal

_SCALARS = {"int": "int", "long": "long", "float": "double", "bool": "bool", "string": "string"}
_DEFAULTS = {"int": "0", "long": "0L", "float": "0.0", "bool": "false", "string": '""'}

_PROGRAM = """using System;
using System.Collections;
using System.Globalization;
using System.Text;

static class LcProgram
{
    static string LcQ(string s)
    {
        var b = new StringBuilder("\\"");
        foreach (var c in s)
        {
            if (c == '"') b.Append("\\\\\\"");
            else if (c == '\\\\') b.Append("\\\\\\\\");
            else if (c < 0x20 || c > 0x7e) b.Append("\\\\u").Append(((int)c).ToString("x4"));
            else b.Append(c);
        }
        return b.Append('"').ToString();
    }

    static string LcJson(object v) => v switch
    {
        null => "null",
        string s => LcQ(s),
        char c => LcQ(c.ToString()),
        bool b => b ? "true" : "false",
        int or long => Convert.ToString(v, CultureInfo.InvariantCulture),
        double d => d.ToString("R", CultureInfo.InvariantCulture),
        IEnumerable e => LcList(e),
        _ => LcQ(v.ToString()),
    };

    static string LcList(IEnumerable items)
    {
        var parts = new System.Collections.Generic.List<string>();
        foreach (var x in items) parts.Add(LcJson(x));
        return "[" + string.Join(",", parts) + "]";
    }

    static void LcEmit(Func<object> run)
    {
        string line;
        try
        {
            line = "{\\"ok\\":true,\\"value\\":" + LcJson(run()) + "}";
        }
        catch (Exception e)
        {
            line = "{\\"ok\\":false,\\"error\\":" + LcQ(e.GetType().Name + ": " + e.Message) + "}";
        }
        Console.WriteLine(line);
        Console.Out.Flush();
    }

    static void Main()
    {
        Console.OutputEncoding = new UTF8Encoding(false);
        Console.WriteLine();
        Console.WriteLine("__MARKER__");
__CASES__
    }
}
""".replace("__MARKER__", MARKER)


class CSharpHarness(TypedHarness):
    language = "csharp"
    label = "C#"

    def entrypoint(self, snake: str) -> str:
        return pascal(snake)

    def type_name(self, t: Type) -> str:
        return f"{self.type_name(t.item)}[]" if t.kind == "list" else _SCALARS[t.kind]

    def literal(self, value: Any, t: Type) -> str:
        if t.kind == "list":
            return f"new {self.type_name(t)} {{ {', '.join(self.literal(v, t.item) for v in value)} }}"
        if t.kind == "string":
            return f'"{escape_string(value, unicode="\\u{:04x}", surrogates=True, extra={"\0": "\\0"})}"'
        if t.kind == "long":
            return f"{int(value)}L"
        return self.scalar_literal(value, t)

    def starter(self, entry: str, signature: Signature | None, param_names: list[str]) -> str:
        assert signature
        params = ", ".join(f"{self.type_name(p.type)} {camel(p.name)}" for p in signature.params)
        returns = signature.returns
        default = f"new {self.type_name(returns.item)}[0]" if returns.kind == "list" else _DEFAULTS[returns.kind]
        hint = (
            '        // Invalid input: throw new ArgumentException("message the tests expect");\n'
            if signature.throws
            else ""
        )
        return (
            "using System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Text;\n\n"
            "public class Solution\n{\n"
            f"    public {self.type_name(returns)} {entry}({params})\n    {{\n"
            f"{hint}        // Write your solution here\n"
            f"        return {default};\n"
            "    }\n}\n"
        )

    def build(self, code: str, entry: str, signature: Signature | None, case_args: list[list[Any]]) -> Program:
        assert signature
        cases = "\n".join(
            f"        LcEmit(() => new Solution().{entry}("
            + ", ".join(self.literal(a, p.type) for a, p in zip(args, signature.params, strict=True))
            + "));"
            for args in case_args
        )
        return Program(
            files={"Program.cs": _PROGRAM.replace("__CASES__", cases), "Solution.cs": code}, solution="Solution.cs"
        )
