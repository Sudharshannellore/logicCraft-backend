from fastapi import APIRouter

from app.api.deps import CurrentUser, Services
from app.schemas.learning import LessonCompletion
from app.schemas.framework_quiz import FrameworkQuiz, FrameworkSummary, PracticeTopic, QuizResult, QuizSubmission

router = APIRouter(tags=["framework practice"])


@router.get("/frameworks", response_model=list[FrameworkSummary], summary="Framework courses to practise")
async def list_frameworks(user_id: CurrentUser, services: Services):
    return await services.framework_quiz.frameworks(user_id)


@router.get("/frameworks/{course_id}/practice", response_model=list[PracticeTopic], summary="A framework's practice quizzes")
async def practice_topics(course_id: str, user_id: CurrentUser, services: Services):
    return await services.framework_quiz.practice_topics(user_id, course_id)


@router.get(
    "/frameworks/{course_id}/challenges",
    response_model=list[FrameworkQuiz],
    summary="Today's daily quiz and the zone bosses of one framework",
)
async def framework_challenges(course_id: str, user_id: CurrentUser, services: Services):
    return await services.framework_quiz.challenges(user_id, course_id)


@router.get("/quizzes/{quiz_id}", response_model=FrameworkQuiz)
async def get_quiz(quiz_id: str, user_id: CurrentUser, services: Services):
    return await services.framework_quiz.get(user_id, quiz_id)


@router.post("/quizzes/{quiz_id}/start", response_model=FrameworkQuiz, summary="Start (or restart) a timed quiz's clock")
async def start_quiz(quiz_id: str, user_id: CurrentUser, services: Services):
    return await services.framework_quiz.start(user_id, quiz_id)


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizResult, summary="Grade answers; the first pass pays XP")
async def submit_quiz(quiz_id: str, body: QuizSubmission, user_id: CurrentUser, services: Services):
    return await services.framework_quiz.submit(user_id, quiz_id, body)


@router.post(
    "/quizzes/{quiz_id}/claim",
    response_model=LessonCompletion,
    summary="Open the next zone when a boss's docs have too little to quiz on (no XP)",
)
async def claim_quiz(quiz_id: str, user_id: CurrentUser, services: Services):
    return await services.framework_quiz.claim(user_id, quiz_id)
