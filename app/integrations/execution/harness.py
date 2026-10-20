"""Wraps a learner's solution in a guard and a tiny test driver.

The guard runs *before* the learner's code and locks the runtime down. The driver then calls the
entry function on every case and prints one marker line followed by JSON results, so the learner's
own prints stay visible as console output. Error line numbers match the learner's code exactly.

Only test *inputs* go into the program; expected outputs never leave the server, so a solution
can't read or fake its way past hidden tests.
"""

import json
from dataclasses import dataclass
from typing import Any

MARKER = "__LOGICRAFT_RESULTS__"
PYTHON_FILENAME = "solution.py"

# Modules that only exist to reach outside the process. Networking is also cut at the socket layer,
# so pure helpers like urllib.parse (which pathlib needs) stay importable.
PYTHON_BLOCKED_MODULES = (
    "ctypes", "_ctypes", "subprocess", "_posixsubprocess", "socket", "_socket", "ssl", "_ssl",
    "multiprocessing", "_multiprocessing", "mmap", "pty", "winreg", "_winapi", "msvcrt", "_testcapi",
    "_testinternalcapi", "_testbuffer", "_testmultiphase", "_xxsubinterpreters", "_interpreters",
)  # fmt: skip
# Audit events that act on the outside world (https://docs.python.org/3/library/audit_events.html).
PYTHON_BLOCKED_EVENTS = (
    "os.system", "os.exec", "os.spawn", "os.posix_spawn", "os.fork", "os.forkpty", "os.kill", "os.killpg",
    "os.startfile", "os.remove", "os.rename", "os.rmdir", "os.mkdir", "os.chmod", "os.chown", "os.chdir",
    "os.link", "os.symlink", "os.truncate", "os.putenv", "os.unsetenv", "os.utime", "os.chflags",
    "os.add_dll_directory", "os.setxattr", "os.removexattr", "subprocess.", "socket.", "ctypes.", "winreg.",
    "msvcrt.", "_winapi.", "shutil.", "webbrowser.", "pty.", "resource.setrlimit", "sys.remote_exec",
    "sqlite3.", "glob.",
)  # fmt: skip

# Installs the guard, then hands back the modules the driver needs. Shared by every Python runner.
_PYTHON_GUARD = """def __cq_guard():
    import json as _json, linecache as _linecache, os as _os, sys as _sys, traceback as _traceback

    # Files may be read only inside the standard library (imports need that) and this run's own folder
    # (the program and any test files written beside it); nothing may be written.
    here = _os.path.dirname(_os.path.abspath(_sys.argv[0]))
    roots = tuple(
        {{_os.path.normcase(_os.path.abspath(p)) + _os.sep for p in (_sys.base_prefix, _sys.base_exec_prefix, here)}}
    )
    blocked_modules = frozenset({blocked_modules})
    blocked_events = {blocked_events}
    write_flags = _os.O_WRONLY | _os.O_RDWR | _os.O_APPEND | _os.O_CREAT | _os.O_TRUNC

    def readable(path):
        if path is None or isinstance(path, int):
            return path is not None  # an already-open file descriptor
        try:
            full = _os.path.normcase(_os.path.abspath(_os.fsdecode(path)))
            return full.startswith(roots) or full + _os.sep in roots  # a root folder itself (e.g. listing it)
        except (TypeError, ValueError):
            return False

    def hook(event, args):
        if event == "open":
            path, mode, flags = args
            writing = any(c in mode for c in "wax+") if isinstance(mode, str) else bool((flags or 0) & write_flags)
            if writing or not readable(path):
                raise PermissionError("File access is disabled in the code runner.")
        elif event in ("os.listdir", "os.scandir"):
            if not readable(args[0]):
                raise PermissionError("File access is disabled in the code runner.")
        elif event == "import":
            if args[0].partition(".")[0] in blocked_modules:
                raise ImportError(f"The {{args[0]}} module is disabled in the code runner.")
        elif event.startswith(blocked_events):
            raise PermissionError(f"{{event}} is disabled in the code runner.")

    _sys.addaudithook(hook)
    return _json, _linecache, _sys, _traceback


__cq_json, __cq_linecache, __cq_sys, __cq_traceback = __cq_guard()
del __cq_guard
"""

_PYTHON = """{guard}
__cq_source = {code}
__cq_linecache.cache["{filename}"] = (len(__cq_source), None, __cq_source.splitlines(True), "{filename}")


def __cq_line(exc):
    lines = [f.lineno for f in __cq_traceback.extract_tb(exc.__traceback__) if f.filename == "{filename}"]
    return f" (line {{lines[-1]}})" if lines else ""


try:
    exec(compile(__cq_source, "{filename}", "exec"), globals())
except Exception as __cq_exc:
    # Show only the learner's own frames, with their real line numbers.
    __cq_traceback.print_exception(type(__cq_exc), __cq_exc, __cq_exc.__traceback__.tb_next)
    __cq_sys.exit(1)


def __cq_main():
    results = []
    for args in __cq_json.loads({cases}):
        try:
            results.append({{"ok": True, "value": {entry}(*args)}})
        except Exception as exc:
            results.append({{"ok": False, "error": type(exc).__name__ + ": " + str(exc) + __cq_line(exc)}})
    __cq_sys.stdout.write("\\n{marker}" + __cq_json.dumps(results, default=repr) + "\\n")


__cq_main()
"""

# Node's permission model (--permission) already denies the filesystem, child processes, workers,
# native addons and process.binding. Node 24 can't deny the network, so the guard removes it here.
JAVASCRIPT_BLOCKED_MODULES = (
    "net", "tls", "dgram", "dns", "http", "https", "http2", "inspector", "child_process", "cluster",
    "worker_threads", "vm", "module", "repl", "trace_events", "wasi",
)  # fmt: skip

# Joined onto line 1, in front of the learner's code, so their line numbers stay exact.
# Every statement ends in `;` because the lines are joined.
_JAVASCRIPT_GUARD = """;(() => {
  'use strict';
  const Module = require('module');
  const blocked = new Set(%s);
  const isBlocked = (id) => blocked.has(String(id).replace(/^node:/, '').split('/')[0]);
  const deny = (id) => Object.assign(new Error(`The ${id} module is disabled in the code runner.`), { code: 'ERR_ACCESS_DENIED' });
  Module.registerHooks({ resolve(specifier, context, nextResolve) { if (isBlocked(specifier)) throw deny(specifier); return nextResolve(specifier, context); } });
  for (const name of ['registerHooks', 'register', '_load', '_resolveFilename']) {
    const original = Module[name];
    if (typeof original !== 'function') continue;
    const guarded = name.startsWith('_') ? function (request, ...rest) { if (isBlocked(request)) throw deny(request); return original.call(this, request, ...rest); } : () => { throw deny('module'); };
    Object.defineProperty(Module, name, { value: guarded, writable: false, configurable: false });
  }
  const getBuiltinModule = process.getBuiltinModule;
  Object.defineProperty(process, 'getBuiltinModule', { value: (id) => { if (isBlocked(id)) throw deny(id); return getBuiltinModule.call(process, id); }, writable: false, configurable: false });
  for (const name of ['fetch', 'WebSocket', 'EventSource', 'XMLHttpRequest']) delete globalThis[name];
})();"""

_JAVASCRIPT_DRIVER = """

;(() => {{
  'use strict'
  const lineOf = (e) => {{
    const match = /main\\.js:(\\d+):/.exec((e && e.stack) || '')
    return match && Number(match[1]) <= {code_lines} ? ` (line ${{match[1]}})` : ''
  }}
  const results = JSON.parse({cases}).map((args) => {{
    try {{
      return {{ ok: true, value: {entry}(...args) }}
    }} catch (e) {{
      return {{ ok: false, error: String((e && e.message) || e) + lineOf(e) }}
    }}
  }})
  process.stdout.write("\\n{marker}" + JSON.stringify(results, (k, v) => (v === undefined ? null : v)) + "\\n")
}})()
"""


@dataclass(frozen=True)
class CaseOutcome:
    ok: bool
    value: Any = None
    error: str | None = None


def python_guard() -> str:
    """Python source that locks the interpreter down; run it before any learner code."""
    return _PYTHON_GUARD.format(
        blocked_modules=repr(PYTHON_BLOCKED_MODULES), blocked_events=repr(PYTHON_BLOCKED_EVENTS)
    )


def javascript_guard() -> str:
    """One-line JavaScript (CommonJS) that removes network and process modules; run it first."""
    return _one_line(_JAVASCRIPT_GUARD % json.dumps(JAVASCRIPT_BLOCKED_MODULES))


def _one_line(source: str) -> str:
    return " ".join(line.strip() for line in source.splitlines())


def build_program(language: str, code: str, entry: str, cases: list[list[Any]]) -> str:
    payload = json.dumps(cases)
    if language == "python":
        return _PYTHON.format(
            guard=python_guard(),
            code=repr(code),
            filename=PYTHON_FILENAME,
            entry=entry,
            cases=repr(payload),
            marker=MARKER,
        )
    if language == "javascript":
        guard = javascript_guard()
        driver = _JAVASCRIPT_DRIVER.format(
            code_lines=code.count("\n") + 1, entry=entry, cases=json.dumps(payload), marker=MARKER
        )
        return f"{guard} {code}{driver}"
    raise ValueError(f"No test harness for {language}")


def parse_output(stdout: str) -> tuple[str, list[CaseOutcome] | None]:
    """Splits the learner's console output from the harness results (None if the harness never reported)."""
    head, sep, tail = stdout.rpartition(MARKER)
    if not sep:
        return stdout, None
    try:
        raw = json.loads(tail.strip().splitlines()[0])
    except (ValueError, IndexError):
        return head, None
    return head.rstrip("\n"), [
        CaseOutcome(ok=r.get("ok", False), value=r.get("value"), error=r.get("error")) for r in raw
    ]


def parse_case_args(test_input: str) -> list[Any]:
    """`[2,7,11,15], 9` -> [[2,7,11,15], 9]"""
    return json.loads(f"[{test_input}]")
