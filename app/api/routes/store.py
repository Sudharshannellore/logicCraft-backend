from fastapi import APIRouter

from app.api.deps import CurrentUser, Services
from app.schemas.store import SubscribeRequest, SubscriptionState, XpPack, XpPlan

router = APIRouter(tags=["store"])


@router.get("/store/plans", response_model=list[XpPlan])
async def list_plans(services: Services):
    return await services.store.list_plans()


@router.get("/store/packs", response_model=list[XpPack])
async def list_packs(services: Services):
    return await services.store.list_packs()


@router.post(
    "/store/packs/{pack_id}/purchase",
    response_model=SubscriptionState,
    summary="Buy a one-time XP pack (demo checkout)",
)
async def buy_pack(pack_id: str, user_id: CurrentUser, services: Services):
    return await services.store.buy_pack(user_id, pack_id)


@router.get("/subscription", response_model=SubscriptionState, summary="Current plan and purchase history")
async def get_subscription(user_id: CurrentUser, services: Services):
    return await services.store.state(user_id)


@router.post("/subscription", response_model=SubscriptionState, summary="Subscribe or switch plans (demo checkout)")
async def subscribe(body: SubscribeRequest, user_id: CurrentUser, services: Services):
    return await services.store.subscribe(user_id, body.plan_id, body.billing)


@router.post("/subscription/cancel", response_model=SubscriptionState, summary="Cancel at the end of the paid period")
async def cancel_subscription(user_id: CurrentUser, services: Services):
    return await services.store.set_cancel_at_period_end(user_id, True)


@router.post("/subscription/resume", response_model=SubscriptionState)
async def resume_subscription(user_id: CurrentUser, services: Services):
    return await services.store.set_cancel_at_period_end(user_id, False)
