from fastapi import APIRouter, Depends

from app.api.deps import get_current_user_id
from app.api.routes import (
    auth,
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

# Public: health, economy config, the landing page's activity feed, and signing in.
for module in (system, auth):
    api_router.include_router(module.router)

# Everything else needs a signed-in player — enforced here once, so no route can forget it.
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
