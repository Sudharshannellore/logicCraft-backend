"""Live challenges: rotating Daily, Speed and weekly Boss challenges, and course-map zone bosses."""

from typing import Literal

from pydantic import Field

from app.schemas.common import CamelModel, Difficulty, EpochMs, XpBalance
from app.schemas.library import ExerciseRunResult

ChallengeKindOut = Literal["daily", "speed", "boss", "zone"]
AttemptStatus = Literal["not_started", "in_progress", "won", "timed_out", "ended"]


class ChallengeStage(CamelModel):
    """One Exercism exercise to beat."""

    slug: str
    name: str
    difficulty: Difficulty
    level: int
    topics: list[str]
    cleared: bool = False
    exercism_url: str


class ChallengeRunner(CamelModel):
    """A player on the fastest-times board."""

    rank: int
    player_id: str
    username: str
    avatar_color: str
    avatar_initials: str
    seconds: int
    is_you: bool


class ChallengeAttempt(CamelModel):
    status: AttemptStatus
    started_at: EpochMs | None = None
    deadline: EpochMs | None = None
    # Solve time, once won.
    seconds: int | None = None
    tries: int = 0


class LiveChallenge(CamelModel):
    id: str
    kind: ChallengeKindOut
    title: str
    description: str
    language: str
    language_name: str
    # False when this server can't run the language's tests: the challenge is solved on exercism.org, untimed.
    gradable: bool
    period: str | None = None
    starts_at: EpochMs | None = None
    # When this challenge rotates out.
    ends_at: EpochMs | None = None
    time_limit_minutes: int
    bonus_xp: int
    boss_name: str | None = None
    boss_sprite: str | None = None
    # Zone bosses only.
    course_id: str | None = None
    boss_id: str | None = None
    # Zone bosses: the zone still has uncleared topics.
    locked: bool = False
    stages: list[ChallengeStage]
    players: int = 0
    winners: int = 0
    fastest: list[ChallengeRunner] = Field(default_factory=list)
    me: ChallengeAttempt
    source_url: str


class ChallengeSubmission(CamelModel):
    slug: str = Field(min_length=1, max_length=100)
    # The language the solution is written in; the challenge itself is the same in all of them.
    language: str = Field("python", max_length=20, pattern="^[a-z]+$")
    # name -> content; only the exercise's own solution files are used.
    files: dict[str, str] = Field(min_length=1)


class ChallengeSubmitResult(CamelModel):
    result: ExerciseRunResult
    challenge: LiveChallenge
    # This stage cleared the challenge (the last stage, inside the time limit).
    won: bool = False
    # The challenge's own bonus — on top of the exercise's first-solve XP in `result.awarded_xp`.
    bonus_xp: int = 0
    balance: XpBalance
