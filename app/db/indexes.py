from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.asynchronous.database import AsyncDatabase

from app.db import collections as c


async def ensure_indexes(db: AsyncDatabase, *, tutorial_cache_ttl_seconds: int, login_lockout_seconds: int) -> None:
    await db[c.USERS].create_indexes(
        [
            IndexModel([("wallet.xp", DESCENDING)]),
            IndexModel([("handle", ASCENDING)], unique=True),
            IndexModel([("email", ASCENDING)], unique=True),
        ]
    )
    await db[c.REFRESH_TOKENS].create_indexes(
        [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0),  # expired tokens disappear
        ]
    )
    await db[c.LOGIN_FAILURES].create_indexes(
        [IndexModel([("first_at", ASCENDING)], expireAfterSeconds=login_lockout_seconds)]
    )
    await db[c.XP_LEDGER].create_indexes(
        [
            # rewardOnce: a reward key can be paid to a user only once.
            IndexModel(
                [("user_id", ASCENDING), ("reward_key", ASCENDING)],
                unique=True,
                partialFilterExpression={"reward_key": {"$type": "string"}},
            ),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("kind", ASCENDING), ("created_at", DESCENDING)]),
        ]
    )
    await db[c.COURSE_PROGRESS].create_indexes(
        [IndexModel([("user_id", ASCENDING), ("course_id", ASCENDING)], unique=True)]
    )
    await db[c.CHALLENGE_ATTEMPTS].create_indexes(
        [
            IndexModel([("challenge_id", ASCENDING), ("won_at", ASCENDING), ("seconds", ASCENDING)]),
            IndexModel([("user_id", ASCENDING)]),
        ]
    )
    await db[c.DAILY_QUESTS].create_indexes([IndexModel([("user_id", ASCENDING), ("date", ASCENDING)], unique=True)])
    await db[c.FRIEND_REQUESTS].create_indexes(
        [
            IndexModel(
                [("from_id", ASCENDING), ("to_id", ASCENDING)],
                unique=True,
                partialFilterExpression={"status": "pending"},
            ),
            IndexModel([("to_id", ASCENDING), ("status", ASCENDING)]),
        ]
    )
    await db[c.FRIENDSHIPS].create_indexes([IndexModel([("users", ASCENDING)])])
    await db[c.DUELS].create_indexes(
        [
            IndexModel([("challenger_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("opponent_id", ASCENDING), ("created_at", DESCENDING)]),
        ]
    )
    await db[c.QUIZ_ATTEMPTS].create_indexes([IndexModel([("user_id", ASCENDING), ("course_id", ASCENDING)])])
    await db[c.PATH_ENROLLMENTS].create_indexes([IndexModel([("user_id", ASCENDING)])])
    await db[c.PURCHASES].create_indexes([IndexModel([("user_id", ASCENDING), ("at", DESCENDING)])])
    await db[c.RESUMES].create_indexes([IndexModel([("user_id", ASCENDING), ("created_at", ASCENDING)])])
    await db[c.JOB_APPLICATIONS].create_indexes([IndexModel([("user_id", ASCENDING), ("applied_at", DESCENDING)])])
    await db[c.SUBMISSIONS].create_indexes([IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)])])
    await db[c.TUTORIAL_CACHE].create_indexes(
        [IndexModel([("created_at", ASCENDING)], expireAfterSeconds=tutorial_cache_ttl_seconds)]
    )
    # Each entry stores its own expiry.
    await db[c.JOB_LISTINGS].create_indexes(
        [
            IndexModel([("languages", ASCENDING), ("posted_at", DESCENDING)]),
            IndexModel([("posted_at", DESCENDING)]),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0),  # closed listings disappear
        ]
    )
    await db[c.JOB_APPLICATIONS].create_indexes([IndexModel([("user_id", ASCENDING), ("job_id", ASCENDING)])])
    await db[c.EXERCISM_CACHE].create_indexes([IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0)])
