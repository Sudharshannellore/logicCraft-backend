"""The learner's resume library, shared by the Resume Builder and the Job Board.

One slot is free; extra slots and premium templates are bought once with XP. Deleting a resume
frees its slot — a bought slot is never lost.
"""

from app.core.clock import new_id, utcnow
from app.core.errors import ConflictError, NotFoundError
from app.domain.economy import FREE_RESUME_SLOTS, MAX_RESUMES, RESUME_SLOT_COST
from app.repositories.catalog import ResumeTemplateRepository
from app.repositories.player_content import ResumeRepository
from app.repositories.users import UserRepository
from app.schemas.resumes import (
    ResumeData,
    ResumeDoc,
    ResumeEntry,
    ResumeLibrary,
    ResumePatch,
    ResumeTemplate,
    SavedResume,
)
from app.schemas.users import UserDoc
from app.services.wallet import WalletService, balance_of


def starter_resume(user: UserDoc) -> ResumeData:
    """A first draft pre-filled from the Logicraft profile. Bullets are plain so AI polish has something to improve."""
    solved = user.stats.code_solved + user.stats.sql_solved
    return ResumeData(
        name=user.username,
        headline="Software Developer",
        email="you@example.com",
        phone="+00 00000 00000",
        location="Your City",
        links=f"github.com/{user.handle.lstrip('@')}",
        skills=[s.name for s in user.skills],
        experience=[
            ResumeEntry(
                id="exp-1",
                title="Software Developer Intern",
                subtitle="Your Company",
                period="2025 – Present",
                bullets=["worked on web features for the dashboard", "fixed bugs reported by the QA team"],
            )
        ],
        projects=[
            ResumeEntry(
                id="proj-1",
                title="Algorithm Practice Portfolio",
                subtitle=", ".join(user.languages[:2]) or "Python, SQL",
                period=str(utcnow().year),
                bullets=[f"solved {solved} coding and SQL problems on Logicraft"],
            )
        ],
        education=[
            ResumeEntry(
                id="edu-1", title="B.Tech in Computer Science", subtitle="Your University", period="2021 – 2025"
            )
        ],
        include_code_quest_stats=True,
    )


def _saved(doc: ResumeDoc) -> SavedResume:
    return SavedResume(
        id=doc.id, title=doc.title, template_id=doc.template_id, data=doc.data, updated_at=doc.updated_at
    )


def _next_title(taken: set[str], base: str) -> str:
    if base not in taken:
        return base
    n = 2
    while f"{base} {n}" in taken:
        n += 1
    return f"{base} {n}"


class ResumeService:
    def __init__(
        self,
        resumes: ResumeRepository,
        templates: ResumeTemplateRepository,
        users: UserRepository,
        wallet: WalletService,
    ):
        self.resumes = resumes
        self.templates = templates
        self.users = users
        self.wallet = wallet

    async def _user(self, user_id: str) -> UserDoc:
        user = await self.users.get(user_id)
        if not user:
            raise NotFoundError("Player not found.")
        return user

    async def _free_template_ids(self) -> list[str]:
        return [t.id for t in await self.templates.list() if t.cost == 0]

    async def _ensure_library(self, user: UserDoc) -> list[ResumeDoc]:
        docs = await self.resumes.for_user(user.id)
        if not docs:
            now = utcnow()
            first = ResumeDoc(
                id=new_id(),
                user_id=user.id,
                title="My resume",
                data=starter_resume(user),
                created_at=now,
                updated_at=now,
            )
            await self.resumes.insert(first)
            await self.users.set_fields(user.id, {"resume_library.active_id": first.id})
            docs = [first]
        return docs

    async def library(self, user_id: str) -> ResumeLibrary:
        user = await self._user(user_id)
        docs = await self._ensure_library(user)
        user = await self._user(user_id)
        lib = user.resume_library
        active = lib.active_id if any(d.id == lib.active_id for d in docs) else docs[0].id
        unlocked = list(dict.fromkeys([*await self._free_template_ids(), *lib.unlocked_templates]))
        return ResumeLibrary(
            resumes=[_saved(d) for d in docs],
            active_id=active,
            extra_slots=lib.extra_slots,
            slot_count=FREE_RESUME_SLOTS + lib.extra_slots,
            max_resumes=MAX_RESUMES,
            slot_cost=RESUME_SLOT_COST,
            unlocked_templates=unlocked,
            balance=balance_of(user),
        )

    async def get(self, user_id: str, resume_id: str) -> SavedResume:
        doc = await self.resumes.get(user_id, resume_id)
        if not doc:
            raise NotFoundError("Resume not found.")
        return _saved(doc)

    async def create(self, user_id: str, source: str) -> ResumeLibrary:
        """Adds a resume (blank, or a copy of the active one), buying a slot with XP when all are used."""
        lib = await self.library(user_id)
        if len(lib.resumes) >= MAX_RESUMES:
            raise ConflictError(f"You can keep up to {MAX_RESUMES} resumes.")
        needs_slot = len(lib.resumes) >= lib.slot_count
        if needs_slot:
            await self.wallet.spend(user_id, RESUME_SLOT_COST, "Extra resume slot")
            await self.users.inc_field(user_id, "resume_library.extra_slots", 1)
        taken = {r.title for r in lib.resumes}
        active = next(r for r in lib.resumes if r.id == lib.active_id)
        now = utcnow()
        if source == "duplicate":
            doc = ResumeDoc(
                id=new_id(),
                user_id=user_id,
                title=_next_title(taken, f"{active.title} (copy)"[:40]),
                template_id=active.template_id,
                data=active.data,
                created_at=now,
                updated_at=now,
            )
        else:
            doc = ResumeDoc(
                id=new_id(),
                user_id=user_id,
                title=_next_title(taken, "New resume"),
                data=starter_resume(await self._user(user_id)),
                created_at=now,
                updated_at=now,
            )
        await self.resumes.insert(doc)
        await self.users.set_fields(user_id, {"resume_library.active_id": doc.id})
        return await self.library(user_id)

    async def update_data(self, user_id: str, resume_id: str, data: ResumeData) -> SavedResume:
        if not await self.resumes.update(user_id, resume_id, {"data": data.model_dump(), "updated_at": utcnow()}):
            raise NotFoundError("Resume not found.")
        return await self.get(user_id, resume_id)

    async def reset(self, user_id: str, resume_id: str) -> SavedResume:
        return await self.update_data(user_id, resume_id, starter_resume(await self._user(user_id)))

    async def patch(self, user_id: str, resume_id: str, patch: ResumePatch) -> SavedResume:
        fields: dict = {}
        if patch.title is not None:
            fields["title"] = patch.title.strip()[:40]
        if patch.template_id is not None:
            lib = await self.library(user_id)
            if patch.template_id not in lib.unlocked_templates:
                raise ConflictError("Unlock that template first.")
            fields["template_id"] = patch.template_id
            fields["updated_at"] = utcnow()
        if fields and not await self.resumes.update(user_id, resume_id, fields):
            raise NotFoundError("Resume not found.")
        return await self.get(user_id, resume_id)

    async def activate(self, user_id: str, resume_id: str) -> ResumeLibrary:
        await self.get(user_id, resume_id)
        await self.users.set_fields(user_id, {"resume_library.active_id": resume_id})
        return await self.library(user_id)

    async def delete(self, user_id: str, resume_id: str) -> ResumeLibrary:
        lib = await self.library(user_id)
        if len(lib.resumes) <= 1:
            raise ConflictError("Keep at least one resume.")
        if not await self.resumes.delete(user_id, resume_id):
            raise NotFoundError("Resume not found.")
        if lib.active_id == resume_id:
            remaining = next(r.id for r in lib.resumes if r.id != resume_id)
            await self.users.set_fields(user_id, {"resume_library.active_id": remaining})
        return await self.library(user_id)

    # --- Templates ---------------------------------------------------------------------------

    async def list_templates(self) -> list[ResumeTemplate]:
        return await self.templates.list()

    async def unlock_template(self, user_id: str, template_id: str) -> ResumeLibrary:
        template = await self.templates.get(template_id)
        if not template:
            raise NotFoundError("Template not found.")
        lib = await self.library(user_id)
        if template_id in lib.unlocked_templates:
            return lib
        await self.wallet.spend(user_id, template.cost, f"Resume template: {template.name}")
        await self.users.add_to_set(user_id, "resume_library.unlocked_templates", template_id)
        return await self.library(user_id)
