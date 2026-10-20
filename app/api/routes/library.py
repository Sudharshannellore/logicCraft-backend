from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Services
from app.schemas.common import Difficulty
from app.schemas.library import ExerciseDetail, ExerciseList, ExerciseRunResult, ExerciseSubmission, LibraryLanguage

router = APIRouter(prefix="/library", tags=["practice library"])


@router.get("/languages", response_model=list[LibraryLanguage], summary="The 13 languages, with exercise counts")
async def list_languages(user_id: CurrentUser, services: Services):
    return await services.library.languages(user_id)


@router.get("/{language}/exercises", response_model=ExerciseList, summary="Live exercises from Exercism")
async def list_exercises(
    language: str,
    user_id: CurrentUser,
    services: Services,
    difficulty: Difficulty | None = None,
    q: str | None = Query(None, max_length=100),
):
    return await services.library.list_exercises(user_id, language, difficulty=difficulty, search=q)


@router.get("/{language}/exercises/{slug}", response_model=ExerciseDetail)
async def get_exercise(language: str, slug: str, user_id: CurrentUser, services: Services):
    return await services.library.get(user_id, language, slug)


@router.post("/{language}/exercises/{slug}/run", response_model=ExerciseRunResult, summary="Run the tests (no XP)")
async def run_exercise(language: str, slug: str, body: ExerciseSubmission, services: Services):
    return await services.library.run(language, slug, body.files)


@router.post(
    "/{language}/exercises/{slug}/submit", response_model=ExerciseRunResult, summary="Run the tests and earn XP"
)
async def submit_exercise(language: str, slug: str, body: ExerciseSubmission, user_id: CurrentUser, services: Services):
    return await services.library.submit(user_id, language, slug, body.files)
