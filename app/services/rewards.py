from app.core.errors import ConflictError, NotFoundError
from app.repositories.catalog import StreakMilestoneRepository
from app.repositories.users import UserRepository
from app.schemas.common import XpAward
from app.schemas.wallet import StreakMilestoneStatus
from app.services.users import current_streak
from app.services.wallet import WalletService


class RewardService:
    """Streak milestones: bonus XP for reaching N days in a row, claimable once each."""

    def __init__(self, milestones: StreakMilestoneRepository, users: UserRepository, wallet: WalletService):
        self.milestones = milestones
        self.users = users
        self.wallet = wallet

    async def streak_milestones(self, user_id: str) -> list[StreakMilestoneStatus]:
        user = await self.users.get(user_id)
        if not user:
            raise NotFoundError("Player not found.")
        streak = current_streak(user)
        return [
            StreakMilestoneStatus(
                days=m.days,
                xp=m.xp,
                claimed=m.days in user.claimed_milestones,
                claimable=streak >= m.days and m.days not in user.claimed_milestones,
            )
            for m in await self.milestones.list()
        ]

    async def claim(self, user_id: str, days: int) -> XpAward:
        milestone = next((m for m in await self.streak_milestones(user_id) if m.days == days), None)
        if not milestone:
            raise NotFoundError("No milestone for that streak length.")
        if milestone.claimed:
            raise ConflictError("Already claimed.")
        if not milestone.claimable:
            raise ConflictError(f"Reach a {days}-day streak to claim this.")
        if not await self.users.add_milestone_if_new(user_id, days):
            raise ConflictError("Already claimed.")
        return await self.wallet.earn(
            user_id,
            milestone.xp,
            f"{days}-day streak reward",
            reward_key=f"streak:{days}",
            activity=f"hit a {days}-day streak",
            sprite="flame",
        )
