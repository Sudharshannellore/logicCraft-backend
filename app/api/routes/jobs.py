from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Services
from app.schemas.jobs import (
    ApplicationUpdate,
    ApplyRequest,
    ApplyResponse,
    Employment,
    Job,
    JobApplication,
    JobLevel,
    JobList,
    WorkMode,
)

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=JobList, summary="Live remote developer jobs from Himalayas and Jobicy")
async def list_jobs(
    services: Services,
    language: str | None = Query(None, max_length=20, pattern="^[a-z]+$", description="A course language id"),
    work_mode: WorkMode | None = Query(None, alias="workMode"),
    employment: Employment | None = None,
    level: JobLevel | None = None,
    q: str | None = Query(None, max_length=100),
):
    return await services.jobs.list_jobs(
        language=language, work_mode=work_mode, employment=employment, level=level, search=q
    )


@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str, services: Services):
    return await services.jobs.get(job_id)


@router.post(
    "/jobs/{job_id}/applications",
    response_model=ApplyResponse,
    summary="Track an application you're making on the job board's site (free)",
)
async def apply_to_job(job_id: str, body: ApplyRequest, user_id: CurrentUser, services: Services):
    return await services.jobs.apply(user_id, job_id, body)


@router.get("/applications", response_model=list[JobApplication])
async def list_applications(user_id: CurrentUser, services: Services):
    return await services.jobs.list_applications(user_id)


@router.patch("/applications/{application_id}", response_model=JobApplication, summary="Update where it stands")
async def update_application(application_id: str, body: ApplicationUpdate, user_id: CurrentUser, services: Services):
    return await services.jobs.update_status(user_id, application_id, body.status)
