from fastapi import APIRouter, Depends

from app.api.deps import get_current_user_id
from app.api.routes import (
    challenges,
    framework_quiz,
    gamification,
    jobs,
    learning,
    library,
    mentor,
    paths,
    practice,
    resumes,
    social,
    sql,
    store,
    system,
    tutorials,
    users,
)

api_router = APIRouter()

api_router.include_router(system.router)

# Everything else acts as the demo player (see get_current_user_id).
protected = (
    users,
    learning,
    tutorials,
    practice,
    library,
    sql,
    challenges,
    framework_quiz,
    gamification,
    social,
    mentor,
    paths,
    store,
    resumes,
    jobs,
)
for module in protected:
    api_router.include_router(module.router, dependencies=[Depends(get_current_user_id)])
