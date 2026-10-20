"""XP subscriptions and one-time packs.

Demo checkout: no payment is taken. Swap `subscribe`/`buy_pack` for a payment provider's
webhook (and credit XP there) when payments are connected.
"""

import calendar
from datetime import datetime

from app.core.clock import as_utc, new_id, utcnow
from app.core.errors import ConflictError, NotFoundError
from app.repositories.catalog import XpPackRepository, XpPlanRepository
from app.repositories.player_content import PurchaseRepository, SubscriptionRepository
from app.schemas.store import (
    Billing,
    PlanId,
    Purchase,
    PurchaseDoc,
    Subscription,
    SubscriptionDoc,
    SubscriptionState,
    XpPack,
    XpPlan,
)
from app.services.wallet import WalletService


def add_months(at: datetime, months: int) -> datetime:
    month_index = at.month - 1 + months
    year, month = at.year + month_index // 12, month_index % 12 + 1
    return at.replace(year=year, month=month, day=min(at.day, calendar.monthrange(year, month)[1]))


class StoreService:
    def __init__(
        self,
        plans: XpPlanRepository,
        packs: XpPackRepository,
        subscriptions: SubscriptionRepository,
        purchases: PurchaseRepository,
        wallet: WalletService,
    ):
        self.plans = plans
        self.packs = packs
        self.subscriptions = subscriptions
        self.purchases = purchases
        self.wallet = wallet

    async def list_plans(self) -> list[XpPlan]:
        return await self.plans.list()

    async def list_packs(self) -> list[XpPack]:
        return await self.packs.list()

    async def _plan(self, plan_id: str) -> XpPlan:
        plan = await self.plans.get(plan_id)
        if not plan:
            raise NotFoundError("Plan not found.")
        return plan

    async def _record(self, user_id: str, label: str, xp: int, price: int, at: datetime | None = None) -> None:
        await self.purchases.insert(
            PurchaseDoc(id=new_id(), user_id=user_id, label=label, xp=xp, price=price, at=at or utcnow())
        )

    async def _catch_up(self, user_id: str) -> SubscriptionDoc | None:
        """Pays monthly drops that came due since the last visit, renews, and ends cancelled plans."""
        sub = await self.subscriptions.get(user_id)
        if not sub:
            return None
        now = utcnow()
        plan = await self._plan(sub.plan_id)
        next_drop, period_end = as_utc(sub.next_drop_at), as_utc(sub.period_ends_at)
        while next_drop <= now:
            if next_drop >= period_end:
                if sub.cancel_at_period_end:
                    await self.subscriptions.delete(user_id)
                    return None
                period_end = add_months(period_end, 12 if sub.billing == "yearly" else 1)
            await self.wallet.credit(user_id, plan.monthly_xp, f"{plan.name} monthly XP drop")
            await self._record(user_id, f"{plan.name} monthly XP drop", plan.monthly_xp, 0, next_drop)
            next_drop = add_months(next_drop, 1)
        if next_drop != as_utc(sub.next_drop_at) or period_end != as_utc(sub.period_ends_at):
            sub = sub.model_copy(update={"next_drop_at": next_drop, "period_ends_at": period_end})
            await self.subscriptions.save(sub)
        return sub

    async def state(self, user_id: str) -> SubscriptionState:
        sub = await self._catch_up(user_id)
        return SubscriptionState(
            subscription=Subscription(**sub.model_dump(exclude={"user_id"})) if sub else None,
            purchases=[Purchase(**p.model_dump(exclude={"user_id"})) for p in await self.purchases.for_user(user_id)],
            balance=await self.wallet.balance(user_id),
        )

    async def subscribe(self, user_id: str, plan_id: PlanId, billing: Billing) -> SubscriptionState:
        """Starts (or switches to) a plan. A fresh period starts and its first month of XP lands right away."""
        plan = await self._plan(plan_id)
        current = await self._catch_up(user_id)
        if current and current.plan_id == plan_id and current.billing == billing and not current.cancel_at_period_end:
            raise ConflictError(f"You're already on {plan.name} ({billing}).")
        now = utcnow()
        await self.subscriptions.save(
            SubscriptionDoc(
                user_id=user_id,
                plan_id=plan_id,
                billing=billing,
                next_drop_at=add_months(now, 1),
                period_ends_at=add_months(now, 12 if billing == "yearly" else 1),
            )
        )
        await self.wallet.credit(user_id, plan.monthly_xp, f"{plan.name} first month XP")
        await self._record(
            user_id,
            f"{'Switched to' if current else 'Subscribed to'} {plan.name} ({billing})",
            plan.monthly_xp,
            plan.price[billing],
            now,
        )
        return await self.state(user_id)

    async def set_cancel_at_period_end(self, user_id: str, cancel: bool) -> SubscriptionState:
        sub = await self._catch_up(user_id)
        if not sub:
            raise NotFoundError("You don't have a subscription.")
        await self.subscriptions.save(sub.model_copy(update={"cancel_at_period_end": cancel}))
        return await self.state(user_id)

    async def buy_pack(self, user_id: str, pack_id: str) -> SubscriptionState:
        pack = await self.packs.get(pack_id)
        if not pack:
            raise NotFoundError("XP pack not found.")
        label = f"{pack.xp:,} XP pack"
        await self.wallet.credit(user_id, pack.xp, label)
        await self._record(user_id, label, pack.xp, pack.price)
        return await self.state(user_id)
