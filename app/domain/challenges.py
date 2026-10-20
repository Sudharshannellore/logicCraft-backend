"""Live challenge rules: which Exercism exercises are today's Daily, Speed and weekly Boss challenges.

Challenges rotate on a fixed UTC schedule — Daily and Speed at 00:00 UTC, the Boss every Monday — and
are picked deterministically from the language's live Exercism track, so every player gets the same
challenge without anything being stored ahead of time.
"""

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Literal

ChallengeKind = Literal["daily", "speed", "boss"]
KINDS: tuple[ChallengeKind, ...] = ("daily", "speed", "boss")


@dataclass(frozen=True)
class ChallengeRule:
    kind: ChallengeKind
    title: str
    description: str
    # One Exercism level band (1–10, inclusive) per stage.
    stages: tuple[tuple[int, int], ...]
    time_limit_minutes: int
    bonus_xp: int
    # Whether a run that timed out can be restarted from stage 1.
    retry: bool


RULES: dict[ChallengeKind, ChallengeRule] = {
    "daily": ChallengeRule(
        "daily",
        "Daily Challenge",
        "One medium exercise, the same for every player today. You get one 30-minute run, so finish before the clock does.",
        ((3, 5),),
        30,
        100,
        retry=False,
    ),
    "speed": ChallengeRule(
        "speed",
        "Speed Round",
        "A quick warm-up exercise. Solve it within 10 minutes; the fastest times today go on the board.",
        ((1, 2),),
        10,
        60,
        retry=False,
    ),
    "boss": ChallengeRule(
        "boss",
        "Weekly Boss",
        "Three exercises in a row (easy, medium, then hard) in one hour. If time runs out, the boss heals and you start again.",
        ((1, 3), (4, 6), (7, 10)),
        60,
        400,
        retry=True,
    ),
}

# The boss of the week gets a name and a look (purely cosmetic).
BOSS_NAMES = (
    "The Null Pointer Hydra",
    "Off-by-One Ogre",
    "The Infinite Loop Lich",
    "Race Condition Wraith",
    "The Segfault Serpent",
    "Memory Leak Mimic",
    "The Deadlock Dragon",
    "Stack Overflow Titan",
    "The Heisenbug Phantom",
    "Spaghetti Code Kraken",
)
BOSS_SPRITES = ("recursionBoss", "bugSlime", "slime")

# Zone bosses on a course map: one exercise per round, at a level that matches the zone.
ZONE_LEVELS = {"easy": (1, 2), "medium": (2, 4), "hard": (4, 6)}
ZONE_MINUTES_PER_ROUND = 15

# Exercises that make poor challenges whatever the language: refactoring katas start out passing, and
# "Hello, World!" is a one-liner.
_UNSUITABLE_TOPICS = {"refactoring"}
_UNSUITABLE_SLUGS = {"hello-world"}


@dataclass(frozen=True)
class Candidate:
    slug: str
    level: int
    topics: Sequence[str] = ()


def period_of(kind: ChallengeKind, now: datetime) -> str:
    """'2026-10-20' for Daily and Speed, ISO week '2026-W43' for the Boss."""
    if kind == "boss":
        year, week, _ = now.isocalendar()
        return f"{year}-W{week:02d}"
    return now.date().isoformat()


def period_bounds(kind: ChallengeKind, period: str) -> tuple[datetime, datetime]:
    """When the period starts and ends (UTC)."""
    if kind == "boss":
        year, week = period.split("-W")
        start = date.fromisocalendar(int(year), int(week), 1)
        length = timedelta(days=7)
    else:
        start = date.fromisoformat(period)
        length = timedelta(days=1)
    begins = datetime.combine(start, time(), UTC)
    return begins, begins + length


_ID = re.compile(r"^(daily|speed)-(\d{4}-\d{2}-\d{2})-([a-z]+)$|^(boss)-(\d{4}-W\d{2})-([a-z]+)$")


def challenge_id(kind: ChallengeKind, period: str, language: str) -> str:
    return f"{kind}-{period}-{language}"


def parse_id(value: str) -> tuple[ChallengeKind, str, str] | None:
    """(kind, period, language) for a well-formed challenge id, else None."""
    match = _ID.match(value)
    if not match:
        return None
    groups = [g for g in match.groups() if g is not None]
    kind, period, language = groups
    try:
        period_bounds(kind, period)  # type: ignore[arg-type]
    except ValueError:
        return None
    return kind, period, language  # type: ignore[return-value]


def _rank(seed: str, slug: str) -> str:
    return hashlib.sha256(f"{seed}|{slug}".encode()).hexdigest()


def shortlist(pool: Sequence[Candidate], seed: str, levels: tuple[int, int], *, exclude: set[str]) -> list[str]:
    """Slugs in the band, in the seed's order. The first one that turns out to work becomes the challenge.

    Ordering by a hash of (seed, slug) keeps a choice stable when the track gains or loses other exercises.
    If the band is empty, it widens one level at a time.
    """
    usable = [
        c
        for c in pool
        if c.slug not in exclude and c.slug not in _UNSUITABLE_SLUGS and not _UNSUITABLE_TOPICS & set(c.topics)
    ]
    low, high = levels
    while True:
        band = [c for c in usable if low <= c.level <= high]
        if band or (low <= 1 and high >= 10) or not usable:
            break
        low, high = max(1, low - 1), min(10, high + 1)
    return [c.slug for c in sorted(band, key=lambda c: _rank(seed, c.slug))]


def pick_boss(seed: str) -> tuple[str, str]:
    digest = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    return BOSS_NAMES[digest % len(BOSS_NAMES)], BOSS_SPRITES[digest // len(BOSS_NAMES) % len(BOSS_SPRITES)]
