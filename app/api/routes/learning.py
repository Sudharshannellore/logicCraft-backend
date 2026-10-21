from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Services
from app.schemas.learning import (
    Course,
    Lesson,
    LessonCompletion,
    LessonResources,
    PathZone,
)

router = APIRouter(tags=["learn"])


@router.get("/courses", response_model=list[Course])
async def list_courses(user_id: CurrentUser, services: Services):
    return await services.learning.list_courses(user_id)


@router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str, user_id: CurrentUser, services: Services):
    return await services.learning.get_course(user_id, course_id)


@router.get("/courses/{course_id}/path", response_model=list[PathZone], summary="World map with this player's progress")
async def get_course_path(course_id: str, user_id: CurrentUser, services: Services):
    return await services.learning.course_path(user_id, course_id)


@router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str, user_id: CurrentUser, services: Services):
    return await services.learning.get_lesson(user_id, lesson_id)


@router.get(
    "/lessons/{lesson_id}/resources",
    response_model=LessonResources,
    summary="Live tutorials for this lesson from external platforms",
)
async def get_lesson_resources(lesson_id: str, services: Services, limit: int = Query(4, ge=1, le=10)):
    return await services.learning.lesson_resources(lesson_id, limit)


@router.post("/lessons/{lesson_id}/complete", response_model=LessonCompletion)
async def complete_lesson(lesson_id: str, user_id: CurrentUser, services: Services):
    return await services.learning.complete_lesson(user_id, lesson_id)
