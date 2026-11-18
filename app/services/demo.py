"""The showcase data.

There is no sign-up or sign-in: every request acts as one shared demo player. On first start the demo player
is created with some progress, alongside a handful of fictional rivals so the leaderboard, friends list and
activity ticker have something to show. Everything here is created once and never overwritten.
"""

import random
from datetime import timedelta

from pymongo.asynchronous.database import AsyncDatabase

from app.core.clock import new_id, today, utcnow
from app.repositories.ledger import LedgerRepository
from app.repositories.social import FriendRequestRepository, FriendshipRepository
from app.repositories.users import UserRepository
from app.schemas.social import FriendRequestDoc
from app.schemas.users import PlayerStats, Skill, StreakState, UserDoc, WalletState
from app.schemas.wallet import LedgerEntry
from app.domain.economy import STARTER_XP
from app.services.users import initials

DEMO_USER_ID = "demo-player"

# id, name, handle, colour, lifetime xp, streak, code solved, sql solved, bosses, languages, skills, friend?
_RIVALS = [
    ("demo-nina", "Nina Rao", "@nina_rao", "#4da3ff", 9400, 21, 112, 38, 6, ["python", "sql"], [("Python", 92), ("SQL", 80), ("Algorithms", 85)], True),
    ("demo-ben", "Ben Cho", "@ben_cho", "#a78bfa", 7200, 12, 86, 24, 4, ["javascript", "typescript"], [("JavaScript", 88), ("TypeScript", 76), ("React", 70)], True),
    ("demo-ana", "Ana Lee", "@ana_lee", "#f5a623", 5600, 9, 64, 18, 3, ["java", "python"], [("Java", 82), ("Data Structures", 74), ("Python", 68)], True),
    ("demo-omar", "Omar Haddad", "@omar_haddad", "#ff5c5c", 4100, 6, 47, 12, 2, ["go", "python"], [("Go", 78), ("Concurrency", 61), ("Python", 66)], True),
    ("demo-priya", "Priya Nair", "@priya_nair", "#3dd68c", 11800, 33, 140, 52, 8, ["python", "rust"], [("Rust", 84), ("Python", 94), ("Algorithms", 90)], False),
    ("demo-leo", "Leo Martins", "@leo_martins", "#7bf542", 2900, 4, 31, 9, 1, ["javascript"], [("JavaScript", 64), ("CSS", 72)], False),
    ("demo-yuki", "Yuki Tanaka", "@yuki_tanaka", "#4da3ff", 6500, 15, 74, 27, 4, ["cpp", "python"], [("C++", 86), ("Algorithms", 83)], False),
    ("demo-sara", "Sara Idris", "@sara_idris", "#a78bfa", 1600, 2, 18, 4, 0, ["python"], [("Python", 55), ("SQL", 40)], False),
    ("demo-tom", "Tom Becker", "@tom_becker", "#f5a623", 3500, 7, 39, 15, 2, ["csharp", "sql"], [("C#", 70), ("SQL", 77)], False),
]

_WINS = [
    ("defeated The Recursion Boss", "skull"),
    ("solved Two Sum", "star"),
    ("cleared a SQL challenge", "gem"),
    ("kept a 7 day streak", "flame"),
    ("solved Binary Search", "star"),
    ("won a Speed Round", "bolt"),
    ("solved Valid Parentheses", "star"),
    ("finished a lesson", "scroll"),
]


def _player(uid: str, name: str, handle: str, color: str, xp: int, streak: int, code: int, sql: int, bosses: int,
            languages: list[str], skills: list[tuple[str, int]], **extra) -> UserDoc:
    solved = code + sql
    return UserDoc(
        id=uid,
        username=name,
        handle=handle,
        email=f"{uid}@logicraft.app",
        password_hash="",  # nobody signs in; kept only because the stored player document has the field
        avatar_color=color,
        avatar_initials=initials(name),
        joined_at=(today() - timedelta(days=30 + xp // 200)).isoformat(),
        last_seen_at=utcnow() - timedelta(minutes=random.randint(0, 50) if xp % 2 else random.randint(120, 2000)),
        wallet=WalletState(xp=xp, lifetime_xp=xp),
        streak=StreakState(current=streak, longest=max(streak, streak + 3), last_active=today().isoformat()),
        stats=PlayerStats(
            code_solved=code,
            sql_solved=sql,
            challenges_won=solved // 4,
            submissions_total=solved * 2,
            submissions_passed=solved,
            solve_seconds_total=solved * 410,
            solves_timed=solved,
            bosses_defeated=bosses,
            speed_records=bosses // 2,
            debug_won=solved // 6,
            duels_played=bosses * 2,
            duels_won=bosses,
        ),
        skills=[Skill(name=n, percent=p) for n, p in skills],
        languages=languages,
        achievements={},
        **extra,
    )


def _ledger(user_id: str, rng: random.Random, count: int) -> list[LedgerEntry]:
    now = utcnow()
    entries = []
    for i in range(count):
        text, sprite = rng.choice(_WINS)
        amount = rng.choice([25, 50, 75, 100, 150])
        entries.append(
            LedgerEntry(
                id=new_id(),
                user_id=user_id,
                kind="earn",
                amount=amount,
                reason=text.capitalize(),
                activity=text,
                sprite=sprite,
                created_at=now - timedelta(hours=rng.randint(1, 24 * 6), minutes=rng.randint(0, 59)),
            )
        )
    return entries


async def ensure_demo_user(db: AsyncDatabase, *, with_data: bool = True) -> None:
    users = UserRepository(db)
    if await users.get(DEMO_USER_ID):
        return
    if not with_data:  # a bare starter player (the tests rely on this)
        await users.insert(
            UserDoc(
                id=DEMO_USER_ID, username="Demo Player", handle="@demo_player", email="demo@logicraft.app",
                password_hash="", avatar_color="#7bf542", avatar_initials="DP", joined_at=today().isoformat(),
                wallet=WalletState(xp=STARTER_XP, lifetime_xp=0),
            )
        )
        return
    rng = random.Random(7)  # the same showcase every time the database is rebuilt
    ledger = LedgerRepository(db)
    now = utcnow()

    demo = _player(
        DEMO_USER_ID, "Demo Player", "@demo_player", "#7bf542", 3000, 5, 24, 8, 1,
        ["python", "javascript", "sql"],
        [("Python", 72), ("JavaScript", 58), ("SQL", 64), ("Algorithms", 49)],
    )
    demo.email = "demo@logicraft.app"
    demo.last_seen_at = now
    demo.wallet = WalletState(xp=3000, lifetime_xp=3000)
    await users.insert(demo)

    friends = FriendshipRepository(db)
    requests = FriendRequestRepository(db)
    for uid, name, handle, color, xp, streak, code, sql, bosses, langs, skills, friend in _RIVALS:
        if not await users.get(uid):
            await users.insert(_player(uid, name, handle, color, xp, streak, code, sql, bosses, langs, skills))
        await ledger.insert_many(_ledger(uid, rng, 6))
        if friend:
            await friends.add(DEMO_USER_ID, uid, now)
    # One request waiting for the demo player to accept, one they have sent.
    await requests.create(FriendRequestDoc(id=new_id(), from_id="demo-yuki", to_id=DEMO_USER_ID, created_at=now))
    await requests.create(FriendRequestDoc(id=new_id(), from_id=DEMO_USER_ID, to_id="demo-priya", created_at=now))
    await ledger.insert_many(_ledger(DEMO_USER_ID, rng, 10))
