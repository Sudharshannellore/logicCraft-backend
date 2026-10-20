from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import CamelModel, EpochMs, XpBalance

ResumeTemplateId = Literal[
    "classic",
    "minimal",
    "ats",
    "professional",
    "harvard",
    "student",
    "developer",
    "typewriter",
    "compact",
    "elegant",
    "bold",
    "executive",
]


class ResumeEntry(CamelModel):
    id: str
    title: str = Field(default="", max_length=200)
    subtitle: str = Field(default="", max_length=200)
    period: str = Field(default="", max_length=80)
    bullets: list[str] = Field(default_factory=list, max_length=20)


class ResumeData(CamelModel):
    name: str = Field(default="", max_length=120)
    headline: str = Field(default="", max_length=160)
    email: str = Field(default="", max_length=160)
    phone: str = Field(default="", max_length=60)
    location: str = Field(default="", max_length=120)
    links: str = Field(default="", max_length=300)
    summary: str = Field(default="", max_length=3000)
    skills: list[str] = Field(default_factory=list, max_length=60)
    experience: list[ResumeEntry] = Field(default_factory=list, max_length=20)
    projects: list[ResumeEntry] = Field(default_factory=list, max_length=20)
    education: list[ResumeEntry] = Field(default_factory=list, max_length=10)
    include_code_quest_stats: bool = True


class ResumeTemplate(CamelModel):
    id: ResumeTemplateId
    name: str
    description: str
    cost: int


class ResumeDoc(BaseModel):
    id: str
    user_id: str
    title: str
    template_id: ResumeTemplateId = "classic"
    data: ResumeData
    created_at: datetime
    updated_at: datetime


class SavedResume(CamelModel):
    id: str
    title: str
    template_id: ResumeTemplateId
    data: ResumeData
    updated_at: EpochMs


class ResumeLibrary(CamelModel):
    resumes: list[SavedResume]
    active_id: str
    extra_slots: int
    slot_count: int
    max_resumes: int
    slot_cost: int
    unlocked_templates: list[ResumeTemplateId]
    balance: XpBalance


class ResumeCreate(CamelModel):
    source: Literal["starter", "duplicate"] = "starter"


class ResumePatch(CamelModel):
    title: str | None = Field(default=None, min_length=1, max_length=40)
    template_id: ResumeTemplateId | None = None


# --- Resume AI ---------------------------------------------------------------------------


class ImproveBulletRequest(CamelModel):
    text: str = Field(min_length=1, max_length=500)


class TextResult(CamelModel):
    text: str
    balance: XpBalance


class ResumeDataRequest(CamelModel):
    data: ResumeData


class SkillsRequest(CamelModel):
    existing: list[str] = Field(default_factory=list)


class SkillsResult(CamelModel):
    skills: list[str]
    balance: XpBalance


class JobTarget(CamelModel):
    role: str
    company: str


class TailorRequest(CamelModel):
    data: ResumeData
    # Either a job from the board, or pasted job text.
    job_id: str | None = None
    job_description: str | None = Field(default=None, max_length=20_000)


class JobMatch(CamelModel):
    score: int
    matched: list[str]
    missing: list[str]


class TailorResult(JobMatch):
    summary: str


class TailorResponse(CamelModel):
    result: TailorResult
    # The resume with the tailoring applied (summary replaced, matching skills first). Nothing is invented.
    tailored_data: ResumeData
    balance: XpBalance


class CoverNoteRequest(CamelModel):
    data: ResumeData
    job_id: str


class MatchRequest(CamelModel):
    data: ResumeData
    job_id: str | None = None
    job_description: str | None = Field(default=None, max_length=20_000)
