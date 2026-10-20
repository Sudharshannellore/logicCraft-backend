from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.common import CamelModel, EpochMs

# earn   = earned XP (counts toward levels and leaderboards)
# credit = spendable XP that wasn't earned: purchases, refunds, duel winnings
# spend  = XP paid for something
LedgerKind = Literal["earn", "credit", "spend"]


class LedgerEntry(BaseModel):
    id: str
    user_id: str
    kind: LedgerKind
    amount: int  # signed: negative for spend
    reason: str
    reward_key: str | None = None
    # Public activity line for the landing-page ticker, e.g. "defeated The Recursion Boss".
    activity: str | None = None
    sprite: str | None = None
    created_at: datetime


class Wallet(CamelModel):
    xp: int
    lifetime_xp: int
    rewarded: list[str]
    claimed_milestones: list[int]


class Transaction(CamelModel):
    id: str
    kind: LedgerKind
    amount: int
    reason: str
    created_at: EpochMs


class StreakMilestone(CamelModel):
    days: int
    xp: int


class StreakMilestoneStatus(StreakMilestone):
    claimed: bool
    claimable: bool
