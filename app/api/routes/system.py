from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.deps import Services
from app.domain import economy
from app.domain.languages import LANGUAGES
from app.schemas.gamification import ActivityEvent, PlatformStats

router = APIRouter(tags=["system"])


class Health(BaseModel):
    status: str
    database: str
    code_executor: str


@router.get("/health", response_model=Health)
async def health(services: Services) -> Health:
    try:
        await services.db.command("ping")
        database = "ok"
    except Exception:
        database = "unreachable"
    return Health(
        status="ok" if database == "ok" else "degraded", database=database, code_executor=services.executor.name
    )


@router.get("/stats", response_model=PlatformStats, summary="Live platform counts (public)")
async def platform_stats(services: Services):
    totals = await services.user_repo.totals()
    return PlatformStats(**totals, languages=len(LANGUAGES))


@router.get("/activity", response_model=list[ActivityEvent], summary="Live feed of players' wins (public)")
async def list_activity(services: Services, limit: int = Query(10, ge=1, le=50)):
    return await services.leaderboard.activity(limit)


@router.get("/config/economy")
async def economy_config() -> dict:
    """Every XP price and payout, so the client never hard-codes them."""
    return {
        "aiAnswerCost": economy.AI_ANSWER_COST,
        "resumeAiCost": {
            "summary": economy.RESUME_AI_COST["summary"],
            "bullet": economy.RESUME_AI_COST["bullet"],
            "skills": economy.RESUME_AI_COST["skills"],
            "tailor": economy.RESUME_AI_COST["tailor"],
            "coverNote": economy.RESUME_AI_COST["cover_note"],
        },
        "freeResumeSlots": economy.FREE_RESUME_SLOTS,
        "resumeSlotCost": economy.RESUME_SLOT_COST,
        "maxResumes": economy.MAX_RESUMES,
        "duelWinBonus": economy.DUEL_WIN_BONUS,
        "duelStakes": list(economy.DUEL_STAKES),
        "duelTimeLimits": list(economy.DUEL_TIME_LIMITS),
    }
