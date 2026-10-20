from typing import Literal

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Services
from app.core.errors import UnprocessableError
from app.schemas.mentor import (
    AIMessage,
    AskRequest,
    AskResponse,
    LessonContextRef,
    ProblemContextRef,
    SuggestionsResponse,
)

router = APIRouter(prefix="/mentor", tags=["quest-ai"])


@router.get("/intro", response_model=list[AIMessage])
async def mentor_intro(services: Services):
    return services.mentor.intro()


@router.get("/suggestions", response_model=SuggestionsResponse, summary="Suggested questions, filtered by what's typed")
async def mentor_suggestions(
    services: Services,
    kind: Literal["problem", "lesson"],
    ref: str = Query(..., description="Problem slug or lesson id"),
    step: str | None = None,
    q: str | None = Query(None, max_length=200, description="What the learner has typed so far"),
    limit: int = Query(4, ge=1, le=20),
):
    if not ref:
        raise UnprocessableError("ref is required.")
    context = (
        ProblemContextRef(kind="problem", problem_slug=ref)
        if kind == "problem"
        else LessonContextRef(kind="lesson", lesson_id=ref, step=step)
    )
    return SuggestionsResponse(suggestions=await services.mentor.suggestions(context, q, limit))


@router.post("/ask", response_model=AskResponse, summary="Ask Quest AI (costs XP)")
async def mentor_ask(body: AskRequest, user_id: CurrentUser, services: Services):
    return await services.mentor.ask(user_id, body)
