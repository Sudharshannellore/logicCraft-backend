"""`python -m app.seed [--reset]` — reload catalog content; --reset also deletes every player and their data."""

import argparse
import asyncio

from app.core.config import get_settings
from app.db import collections as c
from app.db.indexes import ensure_indexes
from app.db.mongo import Mongo
from app.seed.seeder import seed_catalog
from app.services.demo import ensure_demo_user

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
]


async def main(reset: bool) -> None:
    settings = get_settings()
    mongo = Mongo(settings.mongodb_uri, settings.mongodb_db)
    try:
        if reset:  # wipe first, so indexes added since the last seed (e.g. unique emails) can build
            for name in PLAYER_COLLECTIONS:
                await mongo.db[name].delete_many({})
        await ensure_indexes(mongo.db, tutorial_cache_ttl_seconds=settings.tutorial_cache_ttl_seconds)
        await ensure_demo_user(mongo.db, with_data=settings.demo_data)
        await seed_catalog(mongo.db)
        print("Catalog reloaded.")
        if reset:
            print("Every player and their data were deleted; the demo player was recreated.")
    finally:
        await mongo.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Also delete every player and their data.")
    asyncio.run(main(parser.parse_args().reset))
