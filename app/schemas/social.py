from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import CamelModel, EpochMs, XpBalance
from app.schemas.users import Player

# --- Friends -----------------------------------------------------------------------------

AddFriendResult = Literal[
    "sent", "invalid", "self", "not-found", "already-friends", "already-sent", "accepted-incoming"
]


class FriendRequestDoc(BaseModel):
    id: str
    from_id: str
    to_id: str
    status: Literal["pending", "accepted", "declined", "cancelled"] = "pending"
    created_at: datetime
    resolved_at: datetime | None = None


class FriendRequestView(CamelModel):
    player_id: str
    player: Player
    at: EpochMs


class SocialOverview(CamelModel):
    my_id: str
    friends: list[Player]
    incoming_requests: list[FriendRequestView]
    outgoing_requests: list[FriendRequestView]


class FriendRequestCreate(CamelModel):
    player_id: str


class FriendRequestOutcome(CamelModel):
    result: AddFriendResult
    overview: SocialOverview


# --- Duels --------------------------------------------------------------------------------

DuelDocStatus = Literal["pending", "active", "finished", "declined", "cancelled"]
DuelStatus = Literal["pending", "active", "won", "lost", "draw", "declined", "cancelled"]


class DuelPlayerState(BaseModel):
    started_at: datetime | None = None
    finished_at: datetime | None = None
    # Solve time; None while unfinished. `solved=False` with finished_at set = out of time.
    seconds: int | None = None
    solved: bool = False


class DuelDoc(BaseModel):
    id: str
    challenger_id: str
    opponent_id: str
    problem_slug: str
    time_limit_minutes: int
    stake: int
    status: DuelDocStatus = "pending"
    created_at: datetime
    accepted_at: datetime | None = None
    players: dict[str, DuelPlayerState] = Field(default_factory=dict)
    winner_id: str | None = None
    settled: bool = False


class DuelView(CamelModel):
    """A duel as one player sees it — the shape of the frontend's `Duel`."""

    id: str
    friend_id: str
    friend: Player | None = None
    problem_slug: str
    time_limit_minutes: int
    stake: int
    direction: Literal["sent", "received"]
    created_at: EpochMs
    started_at: EpochMs | None = None
    finished_at: EpochMs | None = None
    # Absent until I've finished; null = I didn't solve within the time limit.
    my_seconds: int | None = None
    my_finished: bool = False
    # Hidden (null) until my own result is in.
    friend_seconds: int | None = None
    status: DuelStatus


class DuelCreate(CamelModel):
    friend_id: str
    problem_slug: str
    time_limit_minutes: int
    stake: int = 0


class DuelActionResult(CamelModel):
    duel: DuelView
    balance: XpBalance
