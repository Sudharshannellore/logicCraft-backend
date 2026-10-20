"""Runs an Exercism exercise's own test suite against a learner's solution.

- Python: the track's unittest file, driven by a small runner, inside the sandboxed interpreter.
- JavaScript / TypeScript: the track's Jest spec, run by a dependency-free Jest shim on Node.
- SQL: the track's SQLite shell scripts, replayed by a small worker (assets/sqlite_worker.py).

All of them run in the sandboxed child process (see app/integrations/execution). Every runner reports
one line per test as it finishes, so a hanging test still leaves the earlier results on screen.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from app.integrations.execution import CodeExecutor
from app.integrations.execution.base import ExecutionUnavailable
from app.integrations.execution.harness import javascript_guard, python_guard

TEST_MARKER = "__LOGICRAFT_TEST__"
DONE_MARKER = "__LOGICRAFT_DONE__"
_ASSETS = Path(__file__).parent / "assets"
_MAX_MESSAGE = 1500


@dataclass
class TestOutcome:
    name: str
    status: str  # "pass" | "fail" | "error"
    message: str | None = None


@dataclass
class SuiteResult:
    tests: list[TestOutcome] = field(default_factory=list)
    stdout: str = ""
    error: str | None = None
    runtime_ms: int | None = None

    @property
    def passed(self) -> bool:
        return self.error is None and bool(self.tests) and all(t.status == "pass" for t in self.tests)


def parse_stream(stdout: str) -> tuple[list[TestOutcome], str, bool]:
    """Splits runner output into (test results, the learner's own console output, finished?)."""
    tests: list[TestOutcome] = []
    console: list[str] = []
    finished = False
    for line in stdout.split("\n"):
        if line.startswith(TEST_MARKER):
            try:
                raw = json.loads(line[len(TEST_MARKER) :])
            except ValueError:
                continue
            message = raw.get("message")
            if message and len(message) > _MAX_MESSAGE:
                message = message[:_MAX_MESSAGE] + " …"
            tests.append(
                TestOutcome(name=str(raw.get("name", "test")), status=raw.get("status", "error"), message=message)
            )
        elif line.strip() == DONE_MARKER:
            finished = True
        else:
            console.append(line)
    return tests, "\n".join(console).strip("\n"), finished


# --- Python ---------------------------------------------------------------------------------------

_PYTHON_RUNNER = """{guard}
import importlib as __cq_importlib, os as __cq_os, re as __cq_re, unittest as __cq_unittest

__cq_sys.path.insert(0, __cq_os.path.dirname(__cq_os.path.abspath(__cq_sys.argv[0])))
__CQ_SOLUTIONS = {solutions}


def _cq_emit(name, status, message=None):
    __cq_sys.stdout.write("\\n{marker}" + __cq_json.dumps({{"name": name, "status": status, "message": message}}) + "\\n")
    __cq_sys.stdout.flush()


def _cq_human(test):
    cls = __cq_re.sub(r"Tests?$", "", type(test).__name__)
    cls = __cq_re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", cls).strip().capitalize()
    method = test._testMethodName.removeprefix("test_").replace("_", " ")
    return f"{{cls}} › {{method}}" if cls else method


def _cq_where(tb):
    frames = [f for f in __cq_traceback.extract_tb(tb) if __cq_os.path.basename(f.filename) in __CQ_SOLUTIONS]
    return f" ({{__cq_os.path.basename(frames[-1].filename)}} line {{frames[-1].lineno}})" if frames else ""


class __CqResult(__cq_unittest.TestResult):
    def startTest(self, test):
        super().startTest(test)
        self.__outcome = ("pass", None)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.__outcome = ("fail", str(err[1]))

    def addError(self, test, err):
        super().addError(test, err)
        self.__outcome = ("error", f"{{err[0].__name__}}: {{err[1]}}{{_cq_where(err[2])}}")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None and self.__outcome[0] == "pass":
            failed = issubclass(err[0], test.failureException)
            detail = str(err[1]) if failed else f"{{err[0].__name__}}: {{err[1]}}{{_cq_where(err[2])}}"
            self.__outcome = ("fail" if failed else "error", f"{{subtest._subDescription()}}: {{detail}}")

    def stopTest(self, test):
        super().stopTest(test)
        _cq_emit(_cq_human(test), *self.__outcome)


def __cq_main():
    try:
        for name in __CQ_SOLUTIONS:
            __cq_importlib.import_module(name.removesuffix(".py"))
        tests = __cq_importlib.import_module({test_module!r})
    except BaseException as exc:
        # Show only the learner's own frames: the runner's are noise.
        tb = exc.__traceback__
        while tb is not None and __cq_os.path.basename(tb.tb_frame.f_code.co_filename) not in __CQ_SOLUTIONS:
            tb = tb.tb_next
        __cq_traceback.print_exception(type(exc), exc, tb, limit=8)
        __cq_sys.exit(1)

    suite = __cq_unittest.TestSuite()
    for obj in list(vars(tests).values()):  # classes, then methods, in the order the file defines them
        if isinstance(obj, type) and issubclass(obj, __cq_unittest.TestCase) and obj.__module__ == tests.__name__:
            for method in [m for m in vars(obj) if m.startswith("test")]:
                suite.addTest(obj(method))
    suite.run(__CqResult())
    __cq_sys.stdout.write("\\n{done}\\n")


__cq_main()
"""


def python_bundle(solution: dict[str, str], tests: dict[str, str], extra: dict[str, str]) -> tuple[str, dict[str, str]]:
    test_file = next(iter(tests))
    source = _PYTHON_RUNNER.format(
        guard=python_guard(),
        solutions=repr(sorted(solution)),
        marker=TEST_MARKER,
        done=DONE_MARKER,
        test_module=test_file.removesuffix(".py"),
    )
    return source, {**extra, **tests, **solution}


# --- JavaScript / TypeScript ------------------------------------------------------------------------

_NODE_GUARD = """// Resolve '@jest/globals' to the shim and extensionless relative imports ('./two-fer') to real files.
const __cqModule = require('module')
const __cqPath = require('path')
const __cqUrl = require('url')
const __cqJest = __cqUrl.pathToFileURL(__cqPath.join(__dirname, 'jest.mjs')).href
__cqModule.registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier === '@jest/globals' || specifier === 'expect') return nextResolve(__cqJest, context)
    if (/^\\.\\.?\\//.test(specifier) && !/\\.[cm]?[jt]s$/.test(specifier)) {
      for (const ext of ['.js', '.ts', '.mjs']) {
        try {
          return nextResolve(specifier + ext, context)
        } catch {}
      }
    }
    return nextResolve(specifier, context)
  },
})
"""

_NODE_MAIN = """import './guard.cjs'

const jest = await import(new URL('./jest.mjs', import.meta.url).href)
// Some specs use the Jest globals without importing them.
const { run: _run, ...jestGlobals } = jest
Object.assign(globalThis, jestGlobals)
try {
  await import('./%s')
} catch (error) {
  // The solution (or the spec) didn't load — usually a syntax error.
  console.error(error && error.stack ? error.stack.split('\\n').slice(0, 6).join('\\n') : String(error))
  process.exit(1)
}
await jest.run()
process.stdout.write('\\n%s\\n')
"""


def node_bundle(solution: dict[str, str], tests: dict[str, str], extra: dict[str, str]) -> tuple[str, dict[str, str]]:
    spec = next(iter(tests))
    files = {
        **extra,
        **tests,
        **solution,
        "package.json": '{"type": "module"}',
        "jest.mjs": (_ASSETS / "jest.mjs").read_text(encoding="utf-8"),
        "guard.cjs": _NODE_GUARD + "\n" + javascript_guard() + "\n",
    }
    return _NODE_MAIN % (spec, DONE_MARKER), files


# --- SQL -----------------------------------------------------------------------------------------


def sql_bundle(solution: dict[str, str], tests: dict[str, str], extra: dict[str, str]) -> tuple[str, dict[str, str]]:
    payload = {"entry": next(iter(tests)), "files": {**extra, **tests, **solution}, "solutions": sorted(solution)}
    return (_ASSETS / "sqlite_worker.py").read_text(encoding="utf-8"), {"payload.json": json.dumps(payload)}


# --- Running -------------------------------------------------------------------------------------------

_SAFE_FILE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-]*$")


def _flat(files: dict[str, str]) -> dict[str, str]:
    """Only files that can live in the flat run folder (Exercism Python/JS/TS exercises are flat)."""
    return {name: text for name, text in files.items() if _SAFE_FILE.match(name)}


async def run_suite(
    executor: CodeExecutor,
    language: str,
    solution: dict[str, str],
    tests: dict[str, str],
    extra: dict[str, str],
    *,
    timeout_seconds: float | None = None,
) -> SuiteResult:
    if not tests:
        return SuiteResult(error="This exercise has no tests to run.")
    solution, tests, extra = _flat(solution), _flat(tests), _flat(extra)
    if language == "sql":
        source, files = sql_bundle(solution, tests, extra)
        runtime, entry = "python", "logicraft_sql.py"
    elif language == "python":
        source, files = python_bundle(solution, tests, extra)
        runtime, entry = "python", "logicraft_runner.py"
    else:
        source, files = node_bundle(solution, tests, extra)
        runtime, entry = language, "logicraft_main.mjs"
    try:
        output = await executor.execute(runtime, source, files=files, entry=entry, timeout_seconds=timeout_seconds)
    except ExecutionUnavailable as exc:
        return SuiteResult(error=str(exc))

    results, console, finished = parse_stream(output.stdout)
    error = None
    if output.timed_out:
        error = "Time limit exceeded — look for an infinite loop. Tests after the last result shown didn't run."
    elif not finished:
        error = output.stderr.strip() or "Your code stopped before the tests finished."
    elif language == "sql" and output.stderr.strip():
        error = output.stderr.strip()  # errors in the learner's SQL (the scripts keep going, like the shell)
    elif not results:
        error = "No tests ran."
    return SuiteResult(tests=results, stdout=console, error=error, runtime_ms=output.duration_ms)
