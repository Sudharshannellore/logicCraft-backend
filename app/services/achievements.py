from app.core.clock import utcnow
from app.repositories.catalog import AchievementRepository
from app.repositories.users import UserRepository
from app.schemas.gamification import Achievement
from app.schemas.users import UserDoc


def metrics(user: UserDoc) -> dict[str, int]:
    """Numbers achievement rules can test against."""
    s = user.stats
    return {
        "problems_solved": s.code_solved + s.sql_solved,
        "code_solved": s.code_solved,
        "sql_solved": s.sql_solved,
        "challenges_won": s.challenges_won,
        "bosses_defeated": s.bosses_defeated,
        "speed_records": s.speed_records,
        "debug_won": s.debug_won,
        "duels_won": s.duels_won,
        "longest_streak": user.streak.longest,
        "lifetime_xp": user.wallet.xp,
    }


class AchievementService:
    def __init__(self, catalog: AchievementRepository, users: UserRepository):
        self.catalog = catalog
        self.users = users

    async def evaluate(self, user_id: str) -> list[str]:
        """Unlocks every rule-based achievement the player now qualifies for. Unlocks are permanent."""
        user = await self.users.get(user_id)
        if not user:
            return []
        values = metrics(user)
        now = utcnow()
        newly = {
            a.id: now
            for a in await self.catalog.list()
            if a.rule and a.id not in user.achievements and values.get(a.rule.metric, 0) >= a.rule.threshold
        }
        await self.users.unlock_achievements(user_id, newly)
        return list(newly)

    async def for_user(self, user_id: str) -> list[Achievement]:
        await self.evaluate(user_id)
        user = await self.users.get(user_id)
        unlocked = user.achievements if user else {}
        return [
            Achievement(
                id=a.id,
                icon=a.icon,
                title=a.title,
                description=a.description,
                rarity=a.rarity,
                unlocked=a.id in unlocked,
                unlocked_at=unlocked[a.id].date().isoformat() if a.id in unlocked else None,
            )
            for a in await self.catalog.list()
        ]
