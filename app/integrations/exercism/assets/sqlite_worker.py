"""Runs an Exercism SQLite exercise the way the `sqlite3` command-line shell would. Standard library only.

This file runs as its own sandboxed process (memory, CPU and time limits come from the executor). It
reads `payload.json` from its folder — {"entry": test script, "files": {...}, "solutions": [...]} — and
reports results with the same line protocol as the other Exercism runners.

Exercism's SQL tests are shell scripts: they `.read` other files, `.import` CSV fixtures, run the
learner's SQL, compare the result with the expected rows, and finally write `name, status, message`
rows to `output.json` with `.once`. This emulates the dot-commands they use on an in-memory database,
then reports the rows that were written to `output.json`.

The database never touches disk: ATTACH/DETACH (and so VACUUM INTO) are denied, extensions can't be
loaded, only harmless PRAGMAs are allowed, the SQLite heap is capped and a progress handler stops
runaway queries.
"""

import csv
import io
import json
import os
import re
import sqlite3
import sys
import time

TEST_MARKER = "__LOGICRAFT_TEST__"
DONE_MARKER = "__LOGICRAFT_DONE__"
TIME_LIMIT_SECONDS = 8.0
HEAP_LIMIT_BYTES = 96 * 1024 * 1024
MAX_ROWS = 1000
_ALLOWED_PRAGMAS = {"recursive_triggers", "foreign_keys", "case_sensitive_like"}
_COMMENTS = re.compile(r"--[^\n]*|/\*.*?\*/", re.S)
_MISSING_HINTS = {
    "generate_series": "generate_series isn't available here — build the numbers with WITH RECURSIVE instead.",
}


class TimeLimit(Exception):
    pass


def _authorizer(action, arg1, arg2, db_name, trigger):
    if action in (sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH):
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_PRAGMA and str(arg1).lower() not in _ALLOWED_PRAGMAS:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def _regexp(pattern, value):
    """`value REGEXP pattern`, as the sqlite3 shell's regexp extension provides."""
    if pattern is None or value is None:
        return None
    return 1 if re.search(str(pattern), str(value)) else 0


def normalise(name):
    return name.strip().strip("'\"").removeprefix("./")


def split_statements(text):
    """Splits SQL into complete statements (semicolons in strings, comments and triggers are respected)."""
    statements, start = [], 0
    for i, char in enumerate(text):
        if char == ";" and sqlite3.complete_statement(text[start : i + 1]):
            statements.append(text[start : i + 1])
            start = i + 1
    if _COMMENTS.sub("", text[start:]).strip():
        statements.append(text[start:])
    return statements


def format_table(columns, rows):
    lines = [" | ".join(columns)]
    lines += [" | ".join("NULL" if v is None else str(v) for v in row) for row in rows]
    return "\n".join(lines)


class Shell:
    def __init__(self, files, solution_names):
        self.files = {normalise(k): v for k, v in files.items()}
        self.solution_names = {normalise(n) for n in solution_names}
        self.db = sqlite3.connect(":memory:")
        self.db.execute(f"PRAGMA hard_heap_limit = {HEAP_LIMIT_BYTES}")
        self.db.create_function("regexp", 2, _regexp, deterministic=True)
        self.db.set_authorizer(_authorizer)
        self.deadline = time.monotonic() + TIME_LIMIT_SECONDS
        self.db.set_progress_handler(lambda: 1 if time.monotonic() > self.deadline else 0, 10_000)
        self.output = None  # None = the console
        self.once = None
        self.sinks = {}
        self.learner_errors = []
        self.in_solution = 0
        self.depth = 0

    def run_file(self, name):
        name = normalise(name)
        if name not in self.files:
            raise sqlite3.OperationalError(f"cannot open {name}")
        self.depth += 1
        if self.depth > 10:
            raise sqlite3.OperationalError("too many nested .read commands")
        is_solution = name in self.solution_names
        self.in_solution += is_solution
        try:
            self.run_script(self.files[name])
        finally:
            self.in_solution -= is_solution
            self.depth -= 1

    def run_script(self, text):
        buffer = ""
        for line in text.splitlines(keepends=True):
            if not _COMMENTS.sub("", buffer).strip() and line.lstrip().startswith("."):
                buffer = ""
                self.dot(line.strip())
                continue
            buffer += line
            if sqlite3.complete_statement(buffer):
                for statement in split_statements(buffer):
                    self.execute(statement)
                buffer = ""
        if _COMMENTS.sub("", buffer).strip():
            for statement in split_statements(buffer):
                self.execute(statement)

    def execute(self, sql):
        if not _COMMENTS.sub("", sql).strip():
            return
        try:
            cursor = self.db.execute(sql)
            rows = cursor.fetchmany(MAX_ROWS) if cursor.description else []
        except sqlite3.Error as exc:
            text = str(exc)
            if "interrupted" in text:
                raise TimeLimit from exc
            if "not authorized" in text or "authorization denied" in text:
                text = "that statement isn't allowed here (only in-memory tables can be used)."
            for missing, hint in _MISSING_HINTS.items():
                if missing in text.lower():
                    text = hint
            if self.in_solution:
                self.learner_errors.append(f"Error: {text}")
            else:
                print(f"Error: {text}")
            return
        if cursor.description:
            columns = [d[0] for d in cursor.description]
            sink = self.once or self.output
            self.once = None
            if sink is None or sink.endswith(".md"):  # the console, or the learner's own output file
                print(format_table(columns, rows) + "\n")
            else:
                self.sinks.setdefault(sink, []).append((columns, rows))

    def dot(self, line):
        parts = line.split()
        command, args = parts[0].lower(), parts[1:]
        if command == ".read" and args:
            self.run_file(args[0])
        elif command == ".output":
            self.output = normalise(args[0]) if args else None
        elif command == ".once" and args:
            self.once = normalise(args[0])
        elif command == ".import":
            self.import_csv([a for a in args if not a.startswith("--")])
        elif command == ".print":
            print(" ".join(args))
        # .mode, .headers, .separator, .nullvalue, .timer, .bail, .echo… don't affect results.

    def import_csv(self, args):
        if len(args) < 2:
            return
        name, table = normalise(args[0]), args[1].strip("'\"")
        text = self.files.get(name)
        if text is None:
            raise sqlite3.OperationalError(f"cannot open {name}")
        rows = list(csv.reader(io.StringIO(text)))
        exists = self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
        if not exists:  # like the shell: the first row names the new table's columns
            header, rows = rows[0], rows[1:]
            self.db.execute(f'CREATE TABLE "{table}" ({", ".join(chr(34) + c + chr(34) + " TEXT" for c in header)})')
        width = len(self.db.execute(f'SELECT * FROM "{table}" LIMIT 0').description)
        self.db.executemany(
            f'INSERT INTO "{table}" VALUES ({", ".join("?" for _ in range(width))})',
            [(row + [None] * width)[:width] for row in rows if row],
        )


def emit(name, status, message=None):
    sys.stdout.write("\n" + TEST_MARKER + json.dumps({"name": name, "status": status, "message": message}) + "\n")


def main():
    here = os.path.dirname(os.path.abspath(sys.argv[0]))
    with open(os.path.join(here, "payload.json"), encoding="utf-8") as f:
        payload = json.load(f)
    shell = Shell(payload["files"], payload["solutions"])
    try:
        shell.run_file(payload["entry"])
    except TimeLimit:
        sys.stderr.write("Time limit exceeded — a query ran too long.\n")
        return
    except sqlite3.Error as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return
    for columns, rows in shell.sinks.get("output.json", []):
        index = {c: i for i, c in enumerate(columns)}
        for row in rows:
            passed = "status" in index and row[index["status"]] == "pass"
            message = None if passed or "message" not in index else row[index["message"]]
            emit(str(row[index.get("name", 0)]), "pass" if passed else "fail", message)
    for error in dict.fromkeys(shell.learner_errors):  # unique, in order
        sys.stderr.write(error + "\n")
    sys.stdout.write("\n" + DONE_MARKER + "\n")


main()
