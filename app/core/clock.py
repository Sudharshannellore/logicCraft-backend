"""Time and id helpers. Everything is UTC; services take `now` from here so tests can reason about it."""

import uuid
from datetime import UTC, date, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)


def today() -> date:
    return utcnow().date()


def as_utc(value: datetime) -> datetime:
    """MongoDB hands datetimes back naive (in UTC) — make them aware again."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def to_epoch_ms(value: datetime) -> int:
    return int(as_utc(value).timestamp() * 1000)


def new_id() -> str:
    return str(uuid.uuid4())
