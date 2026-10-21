from app.core.clock import new_id, utcnow
from app.core.errors import NotFoundError
from app.domain import mentor
from app.domain.economy import AI_ANSWER_COST
from app.repositories.catalog import ProblemRepository
from app.schemas.mentor import AIMessage, AskRequest, AskResponse, ContextRef, LessonContextRef
from app.services.learning import LearningService
from app.services.wallet import WalletService

INTRO = AIMessage(
    id="mentor-intro",
    role="ai",
    text="I'm Quest AI. Stuck? Ask for a hint, an explanation, or a walkthrough of an example — each answer costs "
    f"{AI_ANSWER_COST} XP.",
    timestamp="2026-01-01T00:00:00Z",
)


class MentorService:
    def __init__(self, problems: ProblemRepository, learning: LearningService, wallet: WalletService):
        self.problems = problems
        self.learning = learning
        self.wallet = wallet

    async def _context(self, ref: ContextRef) -> mentor.MentorContext:
        if isinstance(ref, LessonContextRef):
            lesson = await self.learning.lesson_content(ref.lesson_id)
            return mentor.LessonContext(
                title=lesson.title,
                concept=lesson.concept,
                explanation=lesson.explanation,
                step=ref.step,
            )
        problem = await self.problems.by_slug(ref.problem_slug)
        if not problem:
            raise NotFoundError("Problem not found.")
        return mentor.ProblemContext(
            title=problem.title,
            description=problem.description,
            tags=problem.tags,
            hints=problem.hints,
            examples=[e.model_dump() for e in problem.examples],
        )

    def intro(self) -> list[AIMessage]:
        return [INTRO]

    async def suggestions(self, ref: ContextRef, typed: str | None, limit: int) -> list[str]:
        pool = mentor.suggested_questions(await self._context(ref))
        return mentor.match_suggestions(pool, typed or "", limit)

    async def ask(self, user_id: str, body: AskRequest) -> AskResponse:
        ctx = await self._context(body.context)
        balance = await self.wallet.spend(user_id, AI_ANSWER_COST, "Quest AI answer")
        now = utcnow().isoformat()
        return AskResponse(
            question=AIMessage(id=new_id(), role="user", text=body.question, timestamp=now),
            answer=AIMessage(
                id=new_id(), role="ai", text=mentor.mentor_reply(body.question, ctx, body.turn), timestamp=now
            ),
            cost=AI_ANSWER_COST,
            balance=balance,
        )
