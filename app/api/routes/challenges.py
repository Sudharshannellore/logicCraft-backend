from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Services
from app.schemas.challenges import ChallengeSubmission, ChallengeSubmitResult, LiveChallenge
from app.schemas.learning import LessonCompletion

router = APIRouter(tags=["challenges"])


@router.get(
    "/challenges",
    response_model=list[LiveChallenge],
    summary="Today's Daily and Speed challenges and this week's Boss, from Exercism",
)
async def list_challenges(
    user_id: CurrentUser, services: Services, language: str = Query("python", max_length=20, pattern="^[a-z]+$")
):
    return await services.challenges.board(user_id, language)


@router.get("/challenges/{challenge_id}", response_model=LiveChallenge)
async def get_challenge(challenge_id: str, user_id: CurrentUser, services: Services):
    return await services.challenges.get(user_id, challenge_id)


@router.post("/challenges/{challenge_id}/start", response_model=LiveChallenge, summary="Start (or restart) your clock")
async def start_challenge(challenge_id: str, user_id: CurrentUser, services: Services):
    return await services.challenges.start(user_id, challenge_id)


@router.post("/challenges/{challenge_id}/submit", response_model=ChallengeSubmitResult)
async def submit_challenge(challenge_id: str, body: ChallengeSubmission, user_id: CurrentUser, services: Services):
    return await services.challenges.submit(user_id, challenge_id, body.slug, body.files)


# --- Zone bosses on a course map -------------------------------------------------------------------


@router.get("/courses/{course_id}/bosses/{boss_id}", response_model=LiveChallenge)
async def get_zone_boss(course_id: str, boss_id: str, user_id: CurrentUser, services: Services):
    return await services.challenges.zone_boss(user_id, course_id, boss_id)


@router.post("/courses/{course_id}/bosses/{boss_id}/start", response_model=LiveChallenge)
async def start_zone_boss(course_id: str, boss_id: str, user_id: CurrentUser, services: Services):
    return await services.challenges.start_zone_boss(user_id, course_id, boss_id)


@router.post("/courses/{course_id}/bosses/{boss_id}/submit", response_model=ChallengeSubmitResult)
async def submit_zone_boss(
    course_id: str, boss_id: str, body: ChallengeSubmission, user_id: CurrentUser, services: Services
):
    return await services.challenges.submit_zone_boss(user_id, course_id, boss_id, body.slug, body.files)


@router.post(
    "/courses/{course_id}/bosses/{boss_id}/claim",
    response_model=LessonCompletion,
    summary="Open the next zone after solving the rounds on exercism.org (languages graded there; no XP)",
)
async def claim_zone_boss(course_id: str, boss_id: str, user_id: CurrentUser, services: Services):
    return await services.challenges.claim_zone_boss(user_id, course_id, boss_id)
