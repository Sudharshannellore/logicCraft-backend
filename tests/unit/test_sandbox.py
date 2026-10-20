"""Escape attempts against the code runner. Each must fail without taking the server down."""

import os
import shutil

import pytest

from app.integrations.execution.harness import build_program, parse_output
from app.integrations.execution.local import LocalExecutor

pytestmark = pytest.mark.asyncio(loop_scope="session")
needs_node = pytest.mark.skipif(not shutil.which("node"), reason="Node.js not installed")


@pytest.fixture(scope="module")
def executor():
    return LocalExecutor(timeout_seconds=3, memory_limit_mb=256)


async def run(executor, language, code):
    output = await executor.execute(language, build_program(language, code, "f", [[]]))
    stdout, outcomes = parse_output(output.stdout)
    return output, stdout, (outcomes[0] if outcomes else None)


@pytest.fixture
def secret_file(tmp_path):
    path = tmp_path / "secrets.env"
    path.write_text("MONGODB_URI=mongodb://admin:hunter2@db")
    return path


# --- Python -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "code", "message"),
    [
        ("write a file", "def f():\n    open('x.txt', 'w').write('hi')\n", "File access is disabled"),
        ("list a directory", "import os\ndef f():\n    return os.listdir('/')\n", "File access is disabled"),
        ("run a shell command", "import os\ndef f():\n    return os.system('whoami')\n", "os.system is disabled"),
        ("subprocess", "def f():\n    import subprocess\n", "subprocess module is disabled"),
        (
            "open a socket",
            "import importlib\ndef f():\n    importlib.import_module('socket')\n",
            "socket module is disabled",
        ),
        ("load native code", "def f():\n    import ctypes\n", "ctypes module is disabled"),
    ],
)
async def test_python_cannot_reach_outside_the_process(executor, label, code, message):
    _, _, outcome = await run(executor, "python", code)
    assert outcome and not outcome.ok and message in outcome.error, label


async def test_python_cannot_read_server_files(executor, secret_file):
    _, _, outcome = await run(executor, "python", f"def f():\n    return open({str(secret_file)!r}).read()\n")
    assert not outcome.ok and "File access is disabled" in outcome.error


async def test_python_sees_none_of_the_servers_environment(executor, monkeypatch):
    monkeypatch.setenv("CQ_SERVER_SECRET", "hunter2")
    _, _, outcome = await run(executor, "python", "import os\ndef f():\n    return dict(os.environ)\n")
    assert "CQ_SERVER_SECRET" not in outcome.value
    assert set(outcome.value) <= {"PATH", "SYSTEMROOT", "TEMP", "TMP", "HOME", "TMPDIR", "LANG"}


async def test_python_memory_and_time_are_capped(executor):
    _, _, outcome = await run(executor, "python", "def f():\n    return len(bytearray(2 * 1024**3))\n")
    assert not outcome.ok and outcome.error.startswith("MemoryError")
    output, _, _ = await run(executor, "python", "def f():\n    while True:\n        pass\n")
    assert output.timed_out and output.stderr == "Time limit exceeded"


async def test_python_output_is_capped(executor):
    output, stdout, _ = await run(executor, "python", "def f():\n    while True:\n        print('x' * 1000)\n")
    assert len(stdout) <= executor.max_output_bytes + 100


async def test_python_stdlib_still_works_and_errors_point_at_the_right_line(executor):
    code = (
        "import collections, dataclasses, functools, heapq, pathlib\n"
        "Point = collections.namedtuple('Point', 'x y')\n"
        "@functools.lru_cache\n"
        "def fib(n):\n"
        "    return n if n < 2 else fib(n - 1) + fib(n - 2)\n"
        "def f():\n"
        "    print('hi')\n"
        "    return [fib(20), heapq.nsmallest(1, [3, 1]), Point(1, 2).y, pathlib.PurePath('a/b').name]\n"
    )
    _, stdout, outcome = await run(executor, "python", code)
    assert stdout == "hi" and outcome.value == [6765, [1], 2, "b"]

    _, _, outcome = await run(executor, "python", "def f():\n    value = None\n    return value.missing\n")
    assert outcome.error.endswith("(line 3)")

    output, _, _ = await run(executor, "python", "x = 1\nraise RuntimeError('boom')\ndef f():\n    pass\n")
    assert 'File "solution.py", line 2' in output.stderr and "boom" in output.stderr
    assert os.sep + "cq-run-" not in output.stderr  # no server paths


# --- JavaScript ----------------------------------------------------------------------------------


@needs_node
@pytest.mark.parametrize(
    ("label", "code", "message"),
    [
        ("child process", "function f() { require('child_process').execSync('whoami') }", "disabled"),
        ("network module", "function f() { require('node:https') }", "disabled"),
        ("builtin backdoor", "function f() { process.getBuiltinModule('net') }", "disabled"),
        ("loader backdoor", "function f() { module.constructor._load('net') }", "disabled"),
        ("hook takeover", "function f() { module.constructor.registerHooks({}) }", "disabled"),
    ],
)
async def test_javascript_cannot_reach_outside_the_process(executor, label, code, message):
    _, _, outcome = await run(executor, "javascript", code)
    assert outcome and not outcome.ok and message in outcome.error, label


@needs_node
async def test_javascript_cannot_read_files_or_fetch(executor, secret_file):
    _, _, outcome = await run(
        executor, "javascript", f"function f() {{ return require('fs').readFileSync({str(secret_file)!r}, 'utf8') }}"
    )
    assert not outcome.ok and "restricted" in outcome.error
    _, _, outcome = await run(executor, "javascript", "function f() { return typeof fetch }")
    assert outcome.value == "undefined"


@needs_node
async def test_javascript_memory_is_capped_and_errors_point_at_the_right_line(executor):
    output, _, _ = await run(
        executor, "javascript", "function f() { const a = []; while (true) a.push(new Array(1e6).fill(1)) }"
    )
    assert "ran out of memory" in output.stderr
    _, stdout, outcome = await run(executor, "javascript", "function f() {\n  console.log('hi')\n  return null.x\n}")
    assert stdout == "hi" and outcome.error.endswith("(line 3)")
