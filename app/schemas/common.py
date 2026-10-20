from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, PlainSerializer
from pydantic.alias_generators import to_camel

from app.core.clock import to_epoch_ms


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# Datetimes go out as epoch milliseconds — the frontend compares them with Date.now().
EpochMs = Annotated[datetime, PlainSerializer(to_epoch_ms, return_type=int, when_used="json")]

Difficulty = Literal["easy", "medium", "hard"]
Language = Literal["python", "javascript", "cpp", "java", "sql"]
NodeState = Literal["completed", "current", "locked"]


class XpBalance(CamelModel):
    """Wallet snapshot returned by any action that spends or earns XP, so the client can update in place."""

    xp: int
    lifetime_xp: int


class XpAward(CamelModel):
    """Result of a first-completion reward: `awarded` is 0 when it was already earned."""

    awarded: int
    balance: XpBalance
