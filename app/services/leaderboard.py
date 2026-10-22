from datetime import timedelta

from app.core.clock import utcnow
from app.domain.progression import level_for
from app.repositories.ledger import LedgerRepository
from app.repositories.social import FriendshipRepository
from app.repositories.users import UserRepository
from app.schemas.gamification import ActivityEvent, LeaderboardEntry, LeaderboardScope
from app.schemas.users import UserDoc

_BADGES = {1: ["👑"], 2: ["🥈"], 3: ["🥉"]}
_PERIODS = {"weekly": timedelta(days=7), "monthly": timedelta(days=30)}


def _win_rate(user: UserDoc) -> int:
    s = user.stats
    return round(100 * s.duels_won / s.duels_played) if s.duels_played else 0


class LeaderboardService:
    def __init__(self, users: UserRepository, ledger: LedgerRepository, friendships: FriendshipRepository):
        self.users = users
        self.ledger = ledger
        self.friendships = friendships

    def _entry(self, rank: int, user: UserDoc, xp: int, me: str) -> LeaderboardEntry:
        return LeaderboardEntry(
            rank=rank,
            user_id=user.id,
            username=user.username,
            avatar_color=user.avatar_color,
            avatar_initials=user.avatar_initials,
            level=level_for(user.wallet.xp),
            xp=xp,
            win_rate=_win_rate(user),
            badges=_BADGES.get(rank, []),
            is_current_user=user.id == me,
        )

    async def leaderboard(self, user_id: str, scope: LeaderboardScope, limit: int) -> list[LeaderboardEntry]:
        """global/friends rank by total XP; weekly/monthly by XP earned in the period."""
        if scope in _PERIODS:
            totals = await self.ledger.earned_since(utcnow() - _PERIODS[scope], limit=limit)
            users = {u.id: u for u in await self.users.get_many([t["user_id"] for t in totals])}
            rows = [(users[t["user_id"]], t["xp"]) for t in totals if t["user_id"] in users]
        else:
            if scope == "friends":
                people = await self.users.get_many([user_id, *await self.friendships.friend_ids(user_id)])
            else:
                people = await self.users.top_by_xp(limit=limit)
            rows = sorted(((u, u.wallet.xp) for u in people), key=lambda r: -r[1])
        return [self._entry(i, u, xp, user_id) for i, (u, xp) in enumerate(rows[:limit], start=1)]

    async def activity(self, limit: int) -> list[ActivityEvent]:
        """Recent public achievements across all players, for the landing page ticker."""
        entries = await self.ledger.recent_activity(limit=limit)
        users = {u.id: u for u in await self.users.get_many(list({e.user_id for e in entries}))}
        return [
            ActivityEvent(
                id=e.id,
                sprite=e.sprite or "star",
                player=users[e.user_id].username,
                action=e.activity or e.reason,
                xp=e.amount,
            )
            for e in entries
            if e.user_id in users
        ]
