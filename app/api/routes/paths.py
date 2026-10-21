from fastapi import APIRouter

from app.api.deps import CurrentUser, Services
from app.schemas.paths import CareerPathDetail, CareerPathSummary

router = APIRouter(prefix="/paths", tags=["career paths"])


@router.get("", response_model=list[CareerPathSummary], summary="Industry paths, suggested ones first")
async def list_paths(user_id: CurrentUser, services: Services):
    return await services.paths.list(user_id)


@router.get("/{path_id}", response_model=CareerPathDetail, summary="A path's courses, in order, with progress")
async def get_path(path_id: str, user_id: CurrentUser, services: Services):
    return await services.paths.get(user_id, path_id)


@router.put("/{path_id}/enroll", response_model=CareerPathDetail, summary="Choose this path")
async def enroll(path_id: str, user_id: CurrentUser, services: Services):
    return await services.paths.enroll(user_id, path_id)


@router.delete("/{path_id}/enroll", response_model=CareerPathDetail, summary="Stop following this path")
async def leave(path_id: str, user_id: CurrentUser, services: Services):
    return await services.paths.leave(user_id, path_id)
