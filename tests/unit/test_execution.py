import json
import shutil

import pytest

from app.integrations.execution.harness import build_program, parse_case_args, parse_output
from app.integrations.execution.local import LocalExecutor
from app.integrations.sql_sandbox import SqlExecutionError, run_query_sync
from app.schemas.sql import SqlColumn, SqlProblem, SqlTable
from app.services.sql import grade

CASES = [parse_case_args("[2,7,11,15], 9"), parse_case_args("[3,3], 6")]


def test_case_args_parse_as_a_call():
    assert parse_case_args('"()[]"') == ["()[]"]
    assert parse_case_args("[[1,3],[2,6]]") == [[[1, 3], [2, 6]]]


def test_output_parsing_keeps_learner_prints_separate():
    stdout, outcomes = parse_output('hello\n\n__LOGICRAFT_RESULTS__[{"ok": true, "value": [0, 1]}]\n')
    assert stdout == "hello"
    assert outcomes[0].value == [0, 1]
    assert parse_output("crashed before reporting")[1] is None


async def test_python_solution_runs_against_cases():
    code = "def two_sum(nums, target):\n    print('checking')\n    return [0, 1]\n"
    output = await LocalExecutor(timeout_seconds=5).execute("python", build_program("python", code, "two_sum", CASES))
    stdout, outcomes = parse_output(output.stdout)
    assert "checking" in stdout
    assert [o.value for o in outcomes] == [[0, 1], [0, 1]]


async def test_runaway_code_times_out():
    code = "def two_sum(nums, target):\n    while True:\n        pass\n"
    output = await LocalExecutor(timeout_seconds=1).execute("python", build_program("python", code, "two_sum", CASES))
    assert output.timed_out


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js not installed")
async def test_javascript_solution_runs_against_cases():
    code = "function twoSum(nums, target) { if (target === 6) throw new Error('nope'); return [0, 1] }"
    output = await LocalExecutor(timeout_seconds=5).execute(
        "javascript", build_program("javascript", code, "twoSum", CASES)
    )
    _, outcomes = parse_output(output.stdout)
    assert outcomes[0].value == [0, 1]
    assert not outcomes[1].ok and "nope" in outcomes[1].error


TABLES = [
    SqlTable(
        name="employees",
        columns=[SqlColumn(name="name", type="VARCHAR"), SqlColumn(name="salary", type="DECIMAL")],
        rows=[{"name": "Ann", "salary": 100.0}, {"name": "Bo", "salary": 50.0}],
    )
]


def test_sandbox_is_read_only():
    with pytest.raises(SqlExecutionError, match="Only SELECT"):
        run_query_sync("DELETE FROM employees", TABLES)
    with pytest.raises(SqlExecutionError, match="one statement"):
        run_query_sync("SELECT 1; DROP TABLE employees", TABLES)
    assert run_query_sync("SELECT name FROM employees WHERE salary > 60", TABLES).rows == [{"name": "Ann"}]


def test_grading_compares_results_not_query_text():
    problem = SqlProblem.model_validate(
        json.loads(
            '{"id":"p","title":"t","slug":"s","difficulty":"easy","xp":1,"acceptanceRate":1,"tags":[],"description":"",'
            '"tablesUsed":["employees"],"starterQuery":"","hints":[],"requiredClauses":[{"fragment":"order by","hint":"Sort it."}],'
            '"expectedColumns":["name"],"expectedRows":[{"name":"Bo"},{"name":"Ann"}],"ordered":true,"successNote":""}'
        )
    )
    right = "select NAME from employees order by salary"
    assert grade(run_query_sync(right, TABLES), problem, right).passed
    wrong_order = "select name from employees order by salary desc"
    assert grade(run_query_sync(wrong_order, TABLES), problem, wrong_order).message.startswith(
        "Right rows, wrong order"
    )
    wrong_columns = "select * from employees"
    assert not grade(run_query_sync(wrong_columns, TABLES), problem, wrong_columns).passed
