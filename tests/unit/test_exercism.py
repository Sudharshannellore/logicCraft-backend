"""Exercism library: the test runners (real sandboxed runs) and the GitHub client (mocked)."""

import json
import shutil
from pathlib import Path

import httpx
import pytest
import respx

from app.integrations.execution.local import LocalExecutor
from app.integrations.exercism.client import ExercismClient
from app.integrations.exercism.runners import parse_stream, run_suite
from app.services.library import difficulty_for, xp_for

node = pytest.mark.skipif(not shutil.which("node"), reason="Node.js not installed")


@pytest.fixture(scope="module")
def executor():
    return LocalExecutor(timeout_seconds=15)


PY_TESTS = {
    "leap_test.py": """import unittest
from leap import leap_year

class LeapTest(unittest.TestCase):
    def test_year_divisible_by_4(self):
        self.assertIs(leap_year(1996), True)

    def test_century_is_not_leap(self):
        self.assertIs(leap_year(1900), False)
"""
}


async def test_python_suite_reports_each_test(executor):
    good = {"leap.py": "def leap_year(y):\n    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)\n"}
    result = await run_suite(executor, "python", good, PY_TESTS, {})
    assert result.passed and [t.name for t in result.tests] == [
        "Leap › year divisible by 4",
        "Leap › century is not leap",
    ]

    naive = {"leap.py": "def leap_year(y):\n    print('checking', y)\n    return y % 4 == 0\n"}
    result = await run_suite(executor, "python", naive, PY_TESTS, {})
    assert [t.status for t in result.tests] == ["pass", "fail"] and "True is not False" in result.tests[1].message
    assert "checking 1996" in result.stdout


async def test_python_errors_point_at_the_learners_line(executor):
    broken = {"leap.py": "def leap_year(y):\n    return y % 0\n"}
    result = await run_suite(executor, "python", broken, PY_TESTS, {})
    assert result.tests[0].status == "error" and "ZeroDivisionError" in result.tests[0].message
    assert "leap.py line 2" in result.tests[0].message

    syntax = {"leap.py": "def leap_year(y)\n    return True\n"}
    result = await run_suite(executor, "python", syntax, PY_TESTS, {})
    assert not result.tests and "SyntaxError" in result.error


async def test_python_solution_cannot_read_outside_its_folder(executor):
    outside = str(Path(__file__).resolve())  # a real file, outside the run folder
    sneaky = {"leap.py": f"def leap_year(y):\n    return open({outside!r}).read()\n"}
    result = await run_suite(executor, "python", sneaky, PY_TESTS, {})
    assert "File access is disabled" in result.tests[0].message


JS_SPEC = {
    "leap.spec.js": """import { describe, expect, test, xtest } from '@jest/globals';
import { isLeap } from './leap';

describe('A leap year', () => {
  test('divisible by 4', () => { expect(isLeap(1996)).toBe(true); });
  xtest('century', () => { expect(isLeap(1900)).toEqual(false); });
  xtest('rejects negatives', () => { expect(() => isLeap(-1)).toThrow('negative'); });
});
"""
}
JS_GOOD = {
    "leap.js": """export const isLeap = (y) => {
  if (y < 0) throw new Error('negative year');
  return y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
};
"""
}


@node
async def test_javascript_suite_runs_the_jest_spec(executor):
    result = await run_suite(executor, "javascript", JS_GOOD, JS_SPEC, {})
    assert result.passed and result.tests[0].name == "A leap year › divisible by 4"

    naive = {"leap.js": "export const isLeap = (y) => y % 4 === 0;\n"}
    result = await run_suite(executor, "javascript", naive, JS_SPEC, {})
    assert [t.status for t in result.tests] == ["pass", "fail", "fail"]
    assert "Expected: false" in result.tests[1].message


@node
async def test_javascript_solution_cannot_use_the_network(executor):
    sneaky = {"leap.js": "import net from 'node:net';\nexport const isLeap = () => true;\n"}
    result = await run_suite(executor, "javascript", sneaky, JS_SPEC, {})
    assert not result.passed and "disabled in the code runner" in result.error


@node
async def test_typescript_suite_runs_with_types_and_enums(executor):
    spec = {
        "leap.test.ts": """import { describe, it, expect } from '@jest/globals'
import { isLeap } from './leap.ts'
describe('leap', () => { it('2000', () => { expect(isLeap(2000)).toBe(true) }) })
"""
    }
    solution = {
        "leap.ts": """enum Rule { Four = 4 }
export function isLeap(year: number): boolean {
  return year % Rule.Four === 0 && (year % 100 !== 0 || year % 400 === 0)
}
"""
    }
    assert (await run_suite(executor, "typescript", solution, spec, {})).passed


SQL_FILES = {
    "create_fixture.sql": "DROP TABLE IF EXISTS leap;\nCREATE TABLE leap (year INT, is_leap BOOL);\n.mode csv\n.import ./data.csv leap\n",
    "data.csv": '1996,""\n1900,""\n2000,""\n',
    "test_setup.sql": ".read ./create_fixture.sql\n.output user_output.md\n.read ./leap.sql\n.output\n"
    "CREATE TABLE tests (name TEXT, status TEXT DEFAULT 'fail', message TEXT, year INT, expected BOOL);\n",
}
SQL_TEST = {
    "leap_test.sql": """.read ./test_setup.sql
INSERT INTO tests (name, year, expected) VALUES ('1996 is leap', 1996, 1), ('1900 is not', 1900, 0), ('2000 is leap', 2000, 1);
UPDATE tests SET status = 'pass' FROM (SELECT year, is_leap FROM leap) AS actual
WHERE (actual.year, actual.is_leap) = (tests.year, tests.expected);
UPDATE tests SET message = 'wrong answer' WHERE status = 'fail';
.mode json
.once './output.json'
SELECT name, status, message FROM tests;
"""
}


async def test_sql_suite_replays_the_sqlite_shell_scripts(executor):
    good = {"leap.sql": "UPDATE leap SET is_leap = (year % 4 = 0 AND (year % 100 != 0 OR year % 400 = 0));\n"}
    result = await run_suite(executor, "sql", good, SQL_TEST, SQL_FILES)
    assert result.passed and [t.name for t in result.tests] == ["1996 is leap", "1900 is not", "2000 is leap"]

    naive = {"leap.sql": "UPDATE leap SET is_leap = year % 4 = 0;\nSELECT 'debug' AS note;\n"}
    result = await run_suite(executor, "sql", naive, SQL_TEST, SQL_FILES)
    assert [t.status for t in result.tests] == ["pass", "fail", "pass"] and result.tests[1].message == "wrong answer"
    assert "debug" in result.stdout


async def test_sql_cannot_touch_the_disk_and_explains_missing_features(executor):
    attach = {"leap.sql": "ATTACH 'stolen.db' AS s;\n"}
    result = await run_suite(executor, "sql", attach, SQL_TEST, SQL_FILES)
    assert "isn't allowed here" in result.error

    series = {"leap.sql": "SELECT value FROM generate_series(1, 3);\n"}
    result = await run_suite(executor, "sql", series, SQL_TEST, SQL_FILES)
    assert "WITH RECURSIVE" in result.error


def test_parse_stream_keeps_console_output_and_partial_results():
    tests, console, finished = parse_stream(
        'hello\n__LOGICRAFT_TEST__{"name": "a", "status": "pass"}\nworld\n__LOGICRAFT_TEST__{"name": "b", "status": "fail", "message": "x"}'
    )
    assert [t.name for t in tests] == ["a", "b"] and console == "hello\nworld" and not finished


def test_difficulty_and_xp_follow_exercism_levels():
    assert [difficulty_for(n) for n in (1, 3, 4, 6, 7, 10)] == ["easy", "easy", "medium", "medium", "hard", "hard"]
    assert (xp_for(1), xp_for(5), xp_for(9)) == (60, 120, 200)


class MemoryCache:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def put(self, key, payload, *, ttl_seconds):
        self.data[key] = payload


RAW = "https://raw.githubusercontent.com/exercism/sqlite/main"


@respx.mock
async def test_client_lists_exercises_and_follows_sql_script_references():
    respx.get(f"{RAW}/config.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "exercises": {
                    "practice": [
                        {"slug": "leap", "name": "Leap", "difficulty": 1, "practices": ["dates"]},
                        {"slug": "old", "name": "Old", "difficulty": 2, "status": "deprecated"},
                    ]
                }
            },
        )
    )
    base = f"{RAW}/exercises/practice/leap"
    meta = {"files": {"solution": ["leap.sql"], "test": ["leap_test.sql"]}, "blurb": "Is it a leap year?"}
    routes = {
        "/.meta/config.json": json.dumps(meta),
        "/leap.sql": "-- write your query",
        "/leap_test.sql": SQL_TEST["leap_test.sql"],
        "/.docs/instructions.md": "# Instructions\nDecide.",
        **{f"/{name}": text for name, text in SQL_FILES.items()},
    }
    for path, text in routes.items():
        respx.get(f"{base}{path}").mock(return_value=httpx.Response(200, text=text))
    respx.get(url__startswith=base).mock(return_value=httpx.Response(404))
    respx.get(url__startswith=f"{RAW}/exercises/practice/missing").mock(return_value=httpx.Response(404))

    async with httpx.AsyncClient() as http:
        client = ExercismClient(http, MemoryCache())
        exercises = await client.exercises("sqlite")
        assert [e.slug for e in exercises] == ["leap"] and exercises[0].topics == ["dates"]

        files = await client.exercise("sqlite", "leap")
        assert files.name == "Leap" and files.instructions.startswith("# Instructions")
        # test_setup.sql was never listed in the metadata — it was found by following `.read` lines.
        assert set(files.support) == {"test_setup.sql", "create_fixture.sql", "data.csv"}
        assert await client.exercise("sqlite", "missing") is None
