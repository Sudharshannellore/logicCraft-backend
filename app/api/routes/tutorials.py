from fastapi import APIRouter, Query

from app.api.deps import Services
from app.core.errors import NotFoundError
from app.schemas.tutorials import ProviderInfo, TutorialReference, TutorialSearchResult

router = APIRouter(prefix="/tutorials", tags=["tutorials"])


@router.get("/providers", response_model=list[ProviderInfo])
async def list_providers(services: Services):
    return services.tutorials.provider_info()


@router.get("/search", response_model=TutorialSearchResult, summary="Search free tutorial platforms at once")
async def search_tutorials(
    services: Services,
    q: str = Query(..., min_length=2, max_length=120, description="Topic, e.g. 'binary search'"),
    language: str | None = Query(None, description="python, javascript, sql, …"),
    providers: list[str] | None = Query(None, description="Limit to these providers (repeatable)"),
    limit: int = Query(5, ge=1, le=20, description="Results per provider"),
):
    return await services.tutorials.search(q, language=language, providers=providers, limit=limit)


@router.get("/reference", response_model=TutorialReference, summary="Short explanation of a concept (MDN / Wikipedia)")
async def get_reference(
    services: Services,
    q: str = Query(..., min_length=2, max_length=120),
    language: str | None = None,
):
    reference = await services.tutorials.reference(q, language)
    if not reference:
        raise NotFoundError("No reference found for that topic.")
    return reference
