from datetime import date, timedelta

from app.core.clock import as_utc, today, utcnow
from app.core.errors import ConflictError, NotFoundError
from app.domain.progression import league_for, level_for, xp_to_next_level
from app.repositories.users import UserRepository
from app.schemas.users import Player, SettingsUpdate, UserDoc, UserProfile, UserSettings, UserStatsOut, UserUpdate


def current_streak(user: UserDoc, day: date | None = None) -> int:
    """The streak still counts if the player was active today or yesterday; otherwise it's broken."""
    if not user.streak.last_active:
        return 0
    last = date.fromisoformat(user.streak.last_active)
    return user.streak.current if last >= (day or today()) - timedelta(days=1) else 0


ONLINE_WINDOW = timedelta(minutes=5)


def is_online(user: UserDoc) -> bool:
    """Used the app in the last few minutes."""
    return user.last_seen_at is not None and utcnow() - as_utc(user.last_seen_at) < ONLINE_WINDOW


def to_player(user: UserDoc) -> Player:
    return Player(
        id=user.id,
        username=user.username,
        avatar_color=user.avatar_color,
        avatar_initials=user.avatar_initials,
        level=level_for(user.wallet.lifetime_xp),
        league=league_for(user.wallet.lifetime_xp).label,
        online=is_online(user),
    )


def initials(name: str) -> str:
    parts = name.split()
    return ("".join(p[0] for p in parts[:2]) if len(parts) > 1 else name[:2]).upper()


class UserService:
    def __init__(self, users: UserRepository):
        self.users = users

    async def get(self, user_id: str) -> UserDoc:
        user = await self.users.get(user_id)
        if not user:
            raise NotFoundError("Player not found.")
        return user

    async def profile(self, user_id: str) -> UserProfile:
        user = await self.get(user_id)
        lifetime = user.wallet.lifetime_xp
        s = user.stats
        return UserProfile(
            id=user.id,
            username=user.username,
            handle=user.handle,
            email=user.email,
            avatar_color=user.avatar_color,
            avatar_initials=user.avatar_initials,
            level=level_for(lifetime),
            xp=lifetime,
            xp_to_next_level=xp_to_next_level(lifetime),
            streak_days=current_streak(user),
            league=league_for(lifetime),
            rank=await self.users.rank_of(lifetime),
            joined_at=user.joined_at,
            stats=UserStatsOut(
                problems_solved=s.code_solved + s.sql_solved,
                challenges_won=s.challenges_won,
                longest_streak=user.streak.longest,
                accuracy=round(100 * s.submissions_passed / s.submissions_total) if s.submissions_total else 0,
                avg_solve_time_seconds=round(s.solve_seconds_total / s.solves_timed) if s.solves_timed else 0,
                languages=user.languages,
            ),
            skills=user.skills,
        )

    async def player(self, player_id: str) -> Player:
        return to_player(await self.get(player_id.strip().lower()))

    async def players(self, limit: int) -> list[Player]:
        return [to_player(u) for u in await self.users.top_by_xp(limit=limit)]

    async def update(self, user_id: str, patch: UserUpdate) -> UserProfile:
        fields = patch.model_dump(exclude_none=True)
        if "handle" in fields and await self.users.handle_taken(fields["handle"], excluding=user_id):
            raise ConflictError("That handle is taken.")
        if "username" in fields:
            fields["avatar_initials"] = initials(fields["username"])
        if fields:
            await self.users.set_fields(user_id, fields)
        return await self.profile(user_id)

    async def settings(self, user_id: str) -> UserSettings:
        return (await self.get(user_id)).settings

    async def update_settings(self, user_id: str, patch: SettingsUpdate) -> UserSettings:
        fields = {f"settings.{k}": v for k, v in patch.model_dump(exclude_none=True).items()}
        user = await self.users.set_fields(user_id, fields) if fields else await self.get(user_id)
        if not user:
            raise NotFoundError("Player not found.")
        return user.settings
