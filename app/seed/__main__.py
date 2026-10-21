"""`python -m app.seed [--reset]` — reload catalog content; --reset also deletes every player and their data."""

import argparse
import asyncio

from app.core.config import get_settings
from app.db import collections as c
from app.db.indexes import ensure_indexes
from app.db.mongo import Mongo
from app.seed.seeder import seed_catalog

PLAYER_COLLECTIONS = [
    c.USERS,
    c.XP_LEDGER,
    c.COURSE_PROGRESS,
    c.CHALLENGE_ATTEMPTS,
    c.DAILY_QUESTS,
    c.FRIEND_REQUESTS,
    c.FRIENDSHIPS,
    c.DUELS,
    c.SUBSCRIPTIONS,
    c.PURCHASES,
    c.RESUMES,
    c.JOB_APPLICATIONS,
    c.SUBMISSIONS,
    c.PATH_ENROLLMENTS,
    c.QUIZ_ATTEMPTS,
    c.REFRESH_TOKENS,
    c.LOGIN_FAILURES,
]


async def main(reset: bool) -> None:
    settings = get_settings()
    mongo = Mongo(settings.mongodb_uri, settings.mongodb_db)
    try:
        if reset:  # wipe first, so indexes added since the last seed (e.g. unique emails) can build
            for name in PLAYER_COLLECTIONS:
                await mongo.db[name].delete_many({})
        await ensure_indexes(
            mongo.db,
            tutorial_cache_ttl_seconds=settings.tutorial_cache_ttl_seconds,
            login_lockout_seconds=settings.login_lockout_minutes * 60,
        )
        await seed_catalog(mongo.db)
        print("Catalog reloaded.")
        if reset:
            print("Every player and their data were deleted. New accounts come from sign-up.")
    finally:
        await mongo.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Also delete every player and their data.")
    asyncio.run(main(parser.parse_args().reset))
