from typing import Literal

from app.schemas.common import CamelModel, XpBalance

Rarity = Literal["common", "rare", "epic", "legendary"]


# --- Daily quests ---------------------------------------------------------------------

QuestEvent = Literal["lesson_completed", "problem_solved", "sql_solved", "boss_stage_cleared", "duel_won"]


class QuestTaskTemplate(CamelModel):
    id: str
    label: str
    event: QuestEvent
    target: int = 1


class QuestTemplate(CamelModel):
    id: str
    title: str
    reward_xp: int
    tasks: list[QuestTaskTemplate]


class QuestTask(CamelModel):
    id: str
    label: str
    done: bool
    progress: int
    target: int


class DailyQuest(CamelModel):
    id: str
    date: str
    title: str
    reward_xp: int
    progress_percent: int
    tasks: list[QuestTask]
    claimed: bool
    claimable: bool


class QuestClaimResult(CamelModel):
    quest: DailyQuest
    awarded: int
    balance: XpBalance


# --- Achievements -----------------------------------------------------------------------


class AchievementRule(CamelModel):
    """Unlocks when `metric` reaches `threshold`. An achievement without a rule (e.g. "League Champion") has no
    automatic trigger yet — it can only be granted by seed data or a future feature."""

    metric: str
    threshold: int


class AchievementDef(CamelModel):
    id: str
    icon: str
    title: str
    description: str
    rarity: Rarity
    rule: AchievementRule | None = None


class Achievement(CamelModel):
    id: str
    icon: str
    title: str
    description: str
    unlocked: bool
    unlocked_at: str | None = None
    rarity: Rarity


# --- Leaderboard & activity --------------------------------------------------------------

LeaderboardScope = Literal["global", "weekly", "monthly", "friends"]


class LeaderboardEntry(CamelModel):
    rank: int
    user_id: str
    username: str
    avatar_color: str
    avatar_initials: str
    level: int
    xp: int
    win_rate: int
    badges: list[str]
    is_current_user: bool = False


class PlatformStats(CamelModel):
    """Real, live counts for the landing page."""

    learners: int
    problems_solved: int
    bosses_defeated: int
    languages: int


class ActivityEvent(CamelModel):
    id: str
    sprite: str
    player: str
    action: str
    xp: int
