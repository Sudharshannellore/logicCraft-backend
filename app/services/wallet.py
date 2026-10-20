"""XP wallet: Logicraft's single currency.

`xp` is the spendable balance. `lifetime_xp` only grows on *earned* XP and drives levels, leagues
and leaderboards — spending never costs a level. Every movement is written to the ledger.
"""

from datetime import date, timedelta

from app.core.clock import new_id, today, utcnow
from app.core.errors import InsufficientXpError, NotFoundError
from app.repositories.ledger import LedgerRepository
from app.repositories.users import UserRepository
from app.schemas.common import XpAward, XpBalance
from app.schemas.users import StreakState, UserDoc
from app.schemas.wallet import LedgerEntry, Transaction, Wallet


def balance_of(user: UserDoc) -> XpBalance:
    return XpBalance(xp=user.wallet.xp, lifetime_xp=user.wallet.lifetime_xp)


def next_streak(streak: StreakState, day: date) -> StreakState:
    """Activity on `day`: same day keeps the streak, the next day extends it, a gap restarts it."""
    last = date.fromisoformat(streak.last_active) if streak.last_active else None
    if last == day:
        return streak
    current = streak.current + 1 if last == day - timedelta(days=1) else 1
    return StreakState(current=current, longest=max(streak.longest, current), last_active=day.isoformat())


class WalletService:
    def __init__(self, users: UserRepository, ledger: LedgerRepository):
        self.users = users
        self.ledger = ledger

    async def _user(self, user_id: str) -> UserDoc:
        user = await self.users.get(user_id)
        if not user:
            raise NotFoundError("Player not found.")
        return user

    async def wallet(self, user_id: str) -> Wallet:
        user = await self._user(user_id)
        return Wallet(
            xp=user.wallet.xp,
            lifetime_xp=user.wallet.lifetime_xp,
            rewarded=sorted(await self.ledger.reward_keys(user_id)),
            claimed_milestones=sorted(user.claimed_milestones),
        )

    async def balance(self, user_id: str) -> XpBalance:
        return balance_of(await self._user(user_id))

    async def has_reward(self, user_id: str, reward_key: str) -> bool:
        return await self.ledger.has_reward(user_id, reward_key)

    async def transactions(self, user_id: str, limit: int) -> list[Transaction]:
        entries = await self.ledger.for_user(user_id, limit=limit)
        return [
            Transaction(id=e.id, kind=e.kind, amount=e.amount, reason=e.reason, created_at=e.created_at)
            for e in entries
        ]

    async def earn(
        self,
        user_id: str,
        amount: int,
        reason: str,
        *,
        reward_key: str | None = None,
        activity: str | None = None,
        sprite: str | None = None,
    ) -> XpAward:
        """Earned XP. With a `reward_key` it pays only once per key (first completion) — `awarded` is 0 after that."""
        if amount <= 0:
            return XpAward(awarded=0, balance=await self.balance(user_id))
        entry = LedgerEntry(
            id=new_id(),
            user_id=user_id,
            kind="earn",
            amount=amount,
            reason=reason,
            reward_key=reward_key,
            activity=activity,
            sprite=sprite,
            created_at=utcnow(),
        )
        if not await self.ledger.insert(entry):
            return XpAward(awarded=0, balance=await self.balance(user_id))
        user = await self.users.add_xp(user_id, amount, lifetime=True)
        if not user:
            await self.ledger.delete(entry.id)
            raise NotFoundError("Player not found.")
        await self._touch_streak(user)
        return XpAward(awarded=amount, balance=balance_of(user))

    async def credit(self, user_id: str, amount: int, reason: str) -> XpBalance:
        """Spendable XP that wasn't earned — purchases, refunds, duel winnings. Never counts toward levels."""
        user = await self.users.add_xp(user_id, amount, lifetime=False)
        if not user:
            raise NotFoundError("Player not found.")
        await self.ledger.insert(
            LedgerEntry(id=new_id(), user_id=user_id, kind="credit", amount=amount, reason=reason, created_at=utcnow())
        )
        return balance_of(user)

    async def spend(self, user_id: str, amount: int, reason: str) -> XpBalance:
        if amount <= 0:
            return await self.balance(user_id)
        user = await self.users.try_spend_xp(user_id, amount)
        if not user:
            current = await self._user(user_id)
            raise InsufficientXpError(amount, current.wallet.xp)
        await self.ledger.insert(
            LedgerEntry(id=new_id(), user_id=user_id, kind="spend", amount=-amount, reason=reason, created_at=utcnow())
        )
        return balance_of(user)

    async def _touch_streak(self, user: UserDoc) -> None:
        updated = next_streak(user.streak, today())
        if updated != user.streak:
            await self.users.set_streak(user.id, updated)
