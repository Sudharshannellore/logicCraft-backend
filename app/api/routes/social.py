from fastapi import APIRouter

from app.api.deps import CurrentUser, Services
from app.schemas.social import (
    DuelActionResult,
    DuelCreate,
    DuelView,
    FriendRequestCreate,
    FriendRequestOutcome,
    SocialOverview,
)

router = APIRouter(tags=["social"])


@router.get("/social", response_model=SocialOverview, summary="My Player ID, friends and pending requests")
async def get_social(user_id: CurrentUser, services: Services):
    return await services.social.overview(user_id)


@router.post("/social/friend-requests", response_model=FriendRequestOutcome)
async def send_friend_request(body: FriendRequestCreate, user_id: CurrentUser, services: Services):
    return await services.social.send_request(user_id, body.player_id)


@router.post("/social/friend-requests/{player_id}/accept", response_model=SocialOverview)
async def accept_friend_request(player_id: str, user_id: CurrentUser, services: Services):
    return await services.social.accept(user_id, player_id)


@router.post("/social/friend-requests/{player_id}/decline", response_model=SocialOverview)
async def decline_friend_request(player_id: str, user_id: CurrentUser, services: Services):
    return await services.social.decline(user_id, player_id)


@router.delete(
    "/social/friend-requests/{player_id}", response_model=SocialOverview, summary="Withdraw a request I sent"
)
async def cancel_friend_request(player_id: str, user_id: CurrentUser, services: Services):
    return await services.social.cancel_request(user_id, player_id)


@router.delete("/social/friends/{player_id}", response_model=SocialOverview)
async def remove_friend(player_id: str, user_id: CurrentUser, services: Services):
    return await services.social.remove_friend(user_id, player_id)


@router.get("/duels", response_model=list[DuelView], tags=["duels"])
async def list_duels(user_id: CurrentUser, services: Services):
    return await services.duels.list_duels(user_id)


@router.post(
    "/duels", response_model=DuelActionResult, tags=["duels"], summary="Challenge a friend (stake is escrowed)"
)
async def create_duel(body: DuelCreate, user_id: CurrentUser, services: Services):
    return await services.duels.create(user_id, body)


@router.get("/duels/{duel_id}", response_model=DuelView, tags=["duels"])
async def get_duel(duel_id: str, user_id: CurrentUser, services: Services):
    return await services.duels.get(user_id, duel_id)


@router.post("/duels/{duel_id}/accept", response_model=DuelActionResult, tags=["duels"])
async def accept_duel(duel_id: str, user_id: CurrentUser, services: Services):
    return await services.duels.accept(user_id, duel_id)


@router.post("/duels/{duel_id}/decline", response_model=DuelActionResult, tags=["duels"])
async def decline_duel(duel_id: str, user_id: CurrentUser, services: Services):
    return await services.duels.decline(user_id, duel_id)


@router.post("/duels/{duel_id}/cancel", response_model=DuelActionResult, tags=["duels"])
async def cancel_duel(duel_id: str, user_id: CurrentUser, services: Services):
    return await services.duels.cancel(user_id, duel_id)


@router.post(
    "/duels/{duel_id}/start", response_model=DuelView, tags=["duels"], summary="Open the board — my clock starts"
)
async def start_duel(duel_id: str, user_id: CurrentUser, services: Services):
    return await services.duels.start(user_id, duel_id)


@router.post("/duels/{duel_id}/forfeit", response_model=DuelView, tags=["duels"], summary="Give up / time ran out")
async def forfeit_duel(duel_id: str, user_id: CurrentUser, services: Services):
    return await services.duels.forfeit(user_id, duel_id)
