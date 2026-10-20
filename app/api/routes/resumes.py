from fastapi import APIRouter

from app.api.deps import CurrentUser, Services
from app.schemas.resumes import (
    CoverNoteRequest,
    ImproveBulletRequest,
    JobMatch,
    MatchRequest,
    ResumeCreate,
    ResumeData,
    ResumeDataRequest,
    ResumeLibrary,
    ResumePatch,
    ResumeTemplate,
    SavedResume,
    SkillsRequest,
    SkillsResult,
    TailorRequest,
    TailorResponse,
    TextResult,
)

router = APIRouter(tags=["resumes"])


@router.get("/resumes", response_model=ResumeLibrary)
async def get_library(user_id: CurrentUser, services: Services):
    return await services.resumes.library(user_id)


@router.post("/resumes", response_model=ResumeLibrary, summary="Add a resume (buys a slot with XP when full)")
async def create_resume(body: ResumeCreate, user_id: CurrentUser, services: Services):
    return await services.resumes.create(user_id, body.source)


@router.get("/resumes/{resume_id}", response_model=SavedResume)
async def get_resume(resume_id: str, user_id: CurrentUser, services: Services):
    return await services.resumes.get(user_id, resume_id)


@router.put("/resumes/{resume_id}/data", response_model=SavedResume)
async def save_resume_data(resume_id: str, body: ResumeData, user_id: CurrentUser, services: Services):
    return await services.resumes.update_data(user_id, resume_id, body)


@router.patch("/resumes/{resume_id}", response_model=SavedResume, summary="Rename or change template")
async def patch_resume(resume_id: str, body: ResumePatch, user_id: CurrentUser, services: Services):
    return await services.resumes.patch(user_id, resume_id, body)


@router.post("/resumes/{resume_id}/activate", response_model=ResumeLibrary)
async def activate_resume(resume_id: str, user_id: CurrentUser, services: Services):
    return await services.resumes.activate(user_id, resume_id)


@router.post("/resumes/{resume_id}/reset", response_model=SavedResume)
async def reset_resume(resume_id: str, user_id: CurrentUser, services: Services):
    return await services.resumes.reset(user_id, resume_id)


@router.delete("/resumes/{resume_id}", response_model=ResumeLibrary)
async def delete_resume(resume_id: str, user_id: CurrentUser, services: Services):
    return await services.resumes.delete(user_id, resume_id)


@router.get("/resume-templates", response_model=list[ResumeTemplate])
async def list_templates(services: Services):
    return await services.resumes.list_templates()


@router.post("/resume-templates/{template_id}/unlock", response_model=ResumeLibrary)
async def unlock_template(template_id: str, user_id: CurrentUser, services: Services):
    return await services.resumes.unlock_template(user_id, template_id)


# --- Resume AI (each action costs XP) -----------------------------------------------


@router.post("/resume-ai/bullet", response_model=TextResult, tags=["resume-ai"])
async def improve_bullet(body: ImproveBulletRequest, user_id: CurrentUser, services: Services):
    return await services.resume_ai.improve_bullet(user_id, body)


@router.post("/resume-ai/summary", response_model=TextResult, tags=["resume-ai"])
async def generate_summary(body: ResumeDataRequest, user_id: CurrentUser, services: Services):
    return await services.resume_ai.summary(user_id, body)


@router.post("/resume-ai/skills", response_model=SkillsResult, tags=["resume-ai"])
async def suggest_skills(body: SkillsRequest, user_id: CurrentUser, services: Services):
    return await services.resume_ai.skills(user_id, body)


@router.post("/resume-ai/tailor", response_model=TailorResponse, tags=["resume-ai"])
async def tailor_resume(body: TailorRequest, user_id: CurrentUser, services: Services):
    return await services.resume_ai.tailor(user_id, body)


@router.post("/resume-ai/cover-note", response_model=TextResult, tags=["resume-ai"])
async def write_cover_note(body: CoverNoteRequest, user_id: CurrentUser, services: Services):
    return await services.resume_ai.cover_note(user_id, body)


@router.post("/resume-ai/match", response_model=JobMatch, tags=["resume-ai"], summary="Keyword match vs a job (free)")
async def match_job(body: MatchRequest, services: Services):
    return await services.resume_ai.match(body)
