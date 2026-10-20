from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Services
from app.schemas.common import XpAward
from app.schemas.users import Player, SettingsUpdate, UserProfile, UserSettings, UserUpdate
from app.schemas.wallet import StreakMilestoneStatus, Transaction, Wallet

router = APIRouter(tags=["players"])


@router.get("/users/me", response_model=UserProfile)
async def get_me(user_id: CurrentUser, services: Services):
    return await services.users.profile(user_id)


@router.patch("/users/me", response_model=UserProfile)
async def update_me(body: UserUpdate, user_id: CurrentUser, services: Services):
    return await services.users.update(user_id, body)


@router.get("/users/me/settings", response_model=UserSettings)
async def get_settings(user_id: CurrentUser, services: Services):
    return await services.users.settings(user_id)


@router.patch("/users/me/settings", response_model=UserSettings)
async def update_settings(body: SettingsUpdate, user_id: CurrentUser, services: Services):
    return await services.users.update_settings(user_id, body)


@router.get("/players", response_model=list[Player], summary="Player directory (find friends by Player ID)")
async def list_players(services: Services, limit: int = Query(50, ge=1, le=200)):
    return await services.users.players(limit)


@router.get("/players/{player_id}", response_model=Player)
async def get_player(player_id: str, services: Services):
    return await services.users.player(player_id)


@router.get("/wallet", response_model=Wallet, tags=["wallet"])
async def get_wallet(user_id: CurrentUser, services: Services):
    return await services.wallet.wallet(user_id)


@router.get("/wallet/transactions", response_model=list[Transaction], tags=["wallet"])
async def list_transactions(user_id: CurrentUser, services: Services, limit: int = Query(50, ge=1, le=200)):
    return await services.wallet.transactions(user_id, limit)


@router.get("/rewards/streak-milestones", response_model=list[StreakMilestoneStatus], tags=["wallet"])
async def list_streak_milestones(user_id: CurrentUser, services: Services):
    return await services.rewards.streak_milestones(user_id)


@router.post("/rewards/streak-milestones/{days}/claim", response_model=XpAward, tags=["wallet"])
async def claim_streak_milestone(days: int, user_id: CurrentUser, services: Services):
    return await services.rewards.claim(user_id, days)
