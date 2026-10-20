"""Runs learner SQL against a fresh in-memory SQLite copy of the practice tables.

Read-only by construction: an authorizer denies every action except reading, and a progress
handler aborts runaway queries. Each run gets its own throwaway database.
"""

import asyncio
import sqlite3
import time
from dataclasses import dataclass

from app.schemas.sql import SqlTable, SqlValue

MAX_ROWS = 500
MAX_VM_STEPS = 5_000_000
_SQLITE_TYPES = {"INT": "INTEGER", "INTEGER": "INTEGER", "DECIMAL": "REAL", "REAL": "REAL", "FLOAT": "REAL"}
_ALLOWED = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}


class SqlExecutionError(Exception):
    pass


@dataclass(frozen=True)
class SqlRun:
    columns: list[str]
    rows: list[dict[str, SqlValue]]
    execution_ms: int
    truncated: bool


def _load(conn: sqlite3.Connection, tables: list[SqlTable]) -> None:
    for table in tables:
        cols = ", ".join(f'"{c.name}" {_SQLITE_TYPES.get(c.type.upper(), "TEXT")}' for c in table.columns)
        conn.execute(f'CREATE TABLE "{table.name}" ({cols})')
        names = [c.name for c in table.columns]
        conn.executemany(
            f'INSERT INTO "{table.name}" VALUES ({", ".join("?" for _ in names)})',
            [[row.get(n) for n in names] for row in table.rows],
        )


def _authorizer(action: int, *_args) -> int:
    return sqlite3.SQLITE_OK if action in _ALLOWED else sqlite3.SQLITE_DENY


def _strip(query: str) -> str:
    # sqlite3 itself rejects a second statement ("You can only execute one statement at a time").
    q = query.strip().rstrip(";").strip()
    if not q:
        raise SqlExecutionError("Write a query first.")
    return q


def run_query_sync(query: str, tables: list[SqlTable]) -> SqlRun:
    sql = _strip(query)
    conn = sqlite3.connect(":memory:")
    try:
        _load(conn, tables)
        conn.set_authorizer(_authorizer)
        steps = 0

        def _guard() -> int:
            nonlocal steps
            steps += 1000
            return 1 if steps > MAX_VM_STEPS else 0

        conn.set_progress_handler(_guard, 1000)
        started = time.perf_counter()
        try:
            cursor = conn.execute(sql)
            fetched = cursor.fetchmany(MAX_ROWS + 1)
        except sqlite3.DatabaseError as exc:
            message = str(exc)
            if "not authorized" in message:
                message = "Only SELECT queries are allowed in the sandbox."
            elif "interrupted" in message:
                message = "Query took too long and was stopped."
            raise SqlExecutionError(message) from exc
        elapsed = max(1, int((time.perf_counter() - started) * 1000))
        columns = [d[0] for d in cursor.description or []]
        rows = [dict(zip(columns, r, strict=True)) for r in fetched[:MAX_ROWS]]
        return SqlRun(columns=columns, rows=rows, execution_ms=elapsed, truncated=len(fetched) > MAX_ROWS)
    finally:
        conn.close()


async def run_query(query: str, tables: list[SqlTable]) -> SqlRun:
    return await asyncio.to_thread(run_query_sync, query, tables)
