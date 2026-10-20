from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Services
from app.schemas.gamification import (
    Achievement,
    DailyQuest,
    LeaderboardEntry,
    LeaderboardScope,
    QuestClaimResult,
)

router = APIRouter(tags=["gamification"])


@router.get("/quests/daily", response_model=DailyQuest)
async def get_daily_quest(user_id: CurrentUser, services: Services):
    return await services.quests.daily(user_id)


@router.post("/quests/daily/claim", response_model=QuestClaimResult)
async def claim_daily_quest(user_id: CurrentUser, services: Services):
    return await services.quests.claim(user_id)


@router.get("/achievements", response_model=list[Achievement])
async def list_achievements(user_id: CurrentUser, services: Services):
    return await services.achievements.for_user(user_id)


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    user_id: CurrentUser,
    services: Services,
    scope: LeaderboardScope = "global",
    limit: int = Query(50, ge=1, le=100),
):
    return await services.leaderboard.leaderboard(user_id, scope, limit)
