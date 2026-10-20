from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import CamelModel, EpochMs, XpBalance
from app.schemas.resumes import ResumeData, ResumeTemplateId

WorkMode = Literal["Remote", "Hybrid", "On-site"]
Employment = Literal["Full-time", "Part-time", "Contract", "Internship"]
JobLevel = Literal["Intern", "Junior", "Mid-level", "Senior"]
JobSource = Literal["Himalayas", "Jobicy"]
# Set by the player: the employer's own process happens on their site, so only the player knows.
ApplicationStatus = Literal["applied", "interviewing", "offer", "rejected"]


class JobLogo(CamelModel):
    sprite: str
    color: str


class Job(CamelModel):
    """A live listing from a job board."""

    id: str
    company: str
    role: str
    location: str
    work_mode: WorkMode
    employment: Employment
    level: JobLevel
    salary: str | None = None
    posted_at: EpochMs
    posted_days_ago: int
    logo: JobLogo
    summary: str
    # Markdown, converted from the board's HTML.
    description: str
    tags: list[str]
    # Course language ids the job asks for.
    languages: list[str]
    source: JobSource
    # The listing on the board, and where Apply must go (the boards' terms).
    source_url: str
    apply_url: str


class JobBoardInfo(CamelModel):
    name: str
    url: str


class JobList(CamelModel):
    jobs: list[Job]
    sources: list[JobBoardInfo]
    # When the oldest feed in this list was fetched.
    updated_at: EpochMs | None = None
    # A board couldn't be reached on the last refresh; older listings are shown.
    stale: bool = False


class JobSnapshot(CamelModel):
    """The job as it was when the player applied — listings close, applications stay."""

    id: str
    role: str
    company: str
    location: str
    source: str
    apply_url: str
    logo: JobLogo


class JobApplicationDoc(BaseModel):
    id: str
    user_id: str
    job_id: str
    job: JobSnapshot | None = None
    applied_at: datetime
    resume: ResumeData
    template_id: ResumeTemplateId
    resume_title: str
    cover_note: str
    tailored: bool
    match_score: int | None
    xp_spent: int
    status: ApplicationStatus = "applied"
    status_updated_at: datetime | None = None


class JobApplication(CamelModel):
    id: str
    job_id: str
    job: JobSnapshot | None
    applied_at: EpochMs
    resume: ResumeData
    template_id: ResumeTemplateId
    resume_title: str
    cover_note: str
    tailored: bool
    match_score: int | None
    # XP spent on Quest AI help while preparing it (applying itself is free).
    xp_spent: int
    status: ApplicationStatus
    status_updated_at: EpochMs | None = None


class ApplyRequest(CamelModel):
    resume_id: str
    # The exact resume prepared for this job when it was tailored; defaults to the saved resume.
    resume: ResumeData | None = None
    cover_note: str = Field(default="", max_length=5000)
    tailored: bool = False
    # XP already spent on AI help (tailoring, cover note) in this flow — shown on the application.
    ai_xp_spent: int = Field(default=0, ge=0, le=1000)


class ApplyResponse(CamelModel):
    application: JobApplication
    balance: XpBalance


class ApplicationUpdate(CamelModel):
    status: ApplicationStatus
