from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import CamelModel

League = Literal["bronze", "silver", "gold", "platinum", "diamond", "master"]


# --- Persistence -------------------------------------------------------------


class WalletState(BaseModel):
    xp: int = 0
    lifetime_xp: int = 0


class StreakState(BaseModel):
    current: int = 0
    longest: int = 0
    last_active: str | None = None  # ISO date


class PlayerStats(BaseModel):
    code_solved: int = 0
    sql_solved: int = 0
    challenges_won: int = 0
    submissions_total: int = 0
    submissions_passed: int = 0
    solve_seconds_total: int = 0
    solves_timed: int = 0
    bosses_defeated: int = 0
    # Speed Rounds won in two minutes or less.
    speed_records: int = 0
    debug_won: int = 0
    duels_played: int = 0
    duels_won: int = 0


class Skill(CamelModel):
    name: str
    percent: int = Field(ge=0, le=100)


class UserSettings(CamelModel):
    email_notifications: bool = True
    sound_effects: bool = True


class ResumeLibraryState(BaseModel):
    active_id: str | None = None
    extra_slots: int = 0
    unlocked_templates: list[str] = Field(default_factory=list)


class UserDoc(BaseModel):
    id: str
    username: str
    handle: str
    email: str  # stored lowercased; unique
    password_hash: str
    # Bumped on password change / sign-out-everywhere: access tokens carrying an older version stop working.
    token_version: int = 0
    avatar_color: str
    avatar_initials: str
    joined_at: str
    # Last time the player used the app (refreshed at most once a minute); drives "online".
    last_seen_at: datetime | None = None
    wallet: WalletState = Field(default_factory=WalletState)
    streak: StreakState = Field(default_factory=StreakState)
    stats: PlayerStats = Field(default_factory=PlayerStats)
    skills: list[Skill] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    settings: UserSettings = Field(default_factory=UserSettings)
    claimed_milestones: list[int] = Field(default_factory=list)
    achievements: dict[str, datetime] = Field(default_factory=dict)
    resume_library: ResumeLibraryState = Field(default_factory=ResumeLibraryState)


# --- API ---------------------------------------------------------------------


class LeagueInfo(CamelModel):
    tier: League
    division: Literal[1, 2, 3]
    label: str


class UserStatsOut(CamelModel):
    problems_solved: int
    challenges_won: int
    longest_streak: int
    accuracy: int
    avg_solve_time_seconds: int
    languages: list[str]


class UserProfile(CamelModel):
    id: str
    username: str
    handle: str
    email: str
    avatar_color: str
    avatar_initials: str
    level: int
    xp: int
    xp_to_next_level: int
    streak_days: int
    league: LeagueInfo
    rank: int
    joined_at: str
    stats: UserStatsOut
    skills: list[Skill]


class Player(CamelModel):
    """Public view of another player (the Friends directory)."""

    id: str
    username: str
    avatar_color: str
    avatar_initials: str
    level: int
    league: str
    online: bool


class UserUpdate(CamelModel):
    username: str | None = Field(default=None, min_length=2, max_length=32)
    handle: str | None = Field(default=None, pattern=r"^@[a-z0-9_]{3,24}$")
    avatar_color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")


class SettingsUpdate(CamelModel):
    email_notifications: bool | None = None
    sound_effects: bool | None = None
