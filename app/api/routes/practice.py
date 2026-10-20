from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Services
from app.schemas.common import Difficulty
from app.schemas.practice import Problem, ProblemSummary, RunCodeRequest, SubmissionResult, SubmitCodeRequest

router = APIRouter(prefix="/problems", tags=["practice"])


@router.get("", response_model=list[ProblemSummary])
async def list_problems(
    user_id: CurrentUser,
    services: Services,
    difficulty: Difficulty | None = None,
    tag: str | None = None,
    search: str | None = Query(None, max_length=100),
):
    return await services.practice.list_problems(user_id, difficulty=difficulty, tag=tag, search=search)


@router.get("/{slug}", response_model=Problem)
async def get_problem(slug: str, user_id: CurrentUser, services: Services):
    return await services.practice.get(user_id, slug)


@router.post("/{slug}/run", response_model=SubmissionResult, summary="Run against the visible test cases")
async def run_code(slug: str, body: RunCodeRequest, services: Services):
    return await services.practice.run(slug, body)


@router.post("/{slug}/submit", response_model=SubmissionResult, summary="Grade against every test case and award XP")
async def submit_code(slug: str, body: SubmitCodeRequest, user_id: CurrentUser, services: Services):
    return await services.practice.submit(user_id, slug, body)
