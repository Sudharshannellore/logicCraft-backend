from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.common import CamelModel, EpochMs, XpBalance

Billing = Literal["monthly", "yearly"]
PlanId = Literal["starter", "pro", "elite"]


class XpPlan(CamelModel):
    id: PlanId
    name: str
    monthly_xp: int
    price: dict[Billing, int]  # INR
    perks: list[str]
    sprite: str
    popular: bool = False


class XpPack(CamelModel):
    id: str
    xp: int
    bonus_percent: int
    price: int  # INR


class SubscriptionDoc(BaseModel):
    user_id: str
    plan_id: PlanId
    billing: Billing
    next_drop_at: datetime
    period_ends_at: datetime
    cancel_at_period_end: bool = False


class Subscription(CamelModel):
    plan_id: PlanId
    billing: Billing
    next_drop_at: EpochMs
    period_ends_at: EpochMs
    cancel_at_period_end: bool


class PurchaseDoc(BaseModel):
    id: str
    user_id: str
    label: str
    xp: int
    price: int
    at: datetime


class Purchase(CamelModel):
    id: str
    label: str
    xp: int
    price: int
    at: EpochMs


class SubscriptionState(CamelModel):
    subscription: Subscription | None
    purchases: list[Purchase]
    balance: XpBalance


class SubscribeRequest(CamelModel):
    plan_id: PlanId
    billing: Billing
