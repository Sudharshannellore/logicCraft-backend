from fastapi import APIRouter

from app.api.deps import CurrentUser, Services
from app.schemas.sql import SqlProblem, SqlProblemSummary, SqlQueryRequest, SqlRunResponse, SqlTable

router = APIRouter(prefix="/sql", tags=["sql"])


@router.get("/tables", response_model=list[SqlTable])
async def list_tables(services: Services):
    return await services.sql.list_tables()


@router.post("/query", response_model=SqlRunResponse, summary="Free-form sandbox query (read-only)")
async def run_query(body: SqlQueryRequest, services: Services):
    return await services.sql.query(body.query)


@router.get("/problems", response_model=list[SqlProblemSummary])
async def list_sql_problems(user_id: CurrentUser, services: Services):
    return await services.sql.list_problems(user_id)


@router.get("/problems/{slug}", response_model=SqlProblem)
async def get_sql_problem(slug: str, user_id: CurrentUser, services: Services):
    return await services.sql.get_problem(user_id, slug)


@router.post("/problems/{slug}/run", response_model=SqlRunResponse)
async def run_sql_problem(slug: str, body: SqlQueryRequest, services: Services):
    return await services.sql.run_problem(slug, body.query)


@router.post("/problems/{slug}/submit", response_model=SqlRunResponse)
async def submit_sql_problem(slug: str, body: SqlQueryRequest, user_id: CurrentUser, services: Services):
    return await services.sql.submit_problem(user_id, slug, body.query)
