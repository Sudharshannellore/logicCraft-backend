from datetime import date

from app.core.clock import today
from app.core.errors import ConflictError, NotFoundError
from app.repositories.catalog import QuestTemplateRepository
from app.repositories.progress import DailyQuestRepository
from app.schemas.gamification import DailyQuest, QuestClaimResult, QuestEvent, QuestTask, QuestTemplate
from app.services.wallet import WalletService


class QuestService:
    """One daily quest per player, rotating through the templates by date. Tasks advance on game events."""

    def __init__(self, templates: QuestTemplateRepository, quests: DailyQuestRepository, wallet: WalletService):
        self.templates = templates
        self.quests = quests
        self.wallet = wallet

    async def _template_for(self, day: date) -> QuestTemplate:
        templates = await self.templates.list()
        if not templates:
            raise NotFoundError("No quests are configured.")
        return templates[day.toordinal() % len(templates)]

    async def _load(self, user_id: str, day: date) -> tuple[dict, QuestTemplate]:
        fallback = await self._template_for(day)
        doc = await self.quests.get_or_create(user_id, day.isoformat(), fallback.id)
        template = await self.templates.get(doc["template_id"]) or fallback
        return doc, template

    @staticmethod
    def _view(doc: dict, template: QuestTemplate) -> DailyQuest:
        progress = doc.get("progress", {})
        tasks = [
            QuestTask(
                id=t.id,
                label=t.label,
                target=t.target,
                progress=min(t.target, progress.get(t.id, 0)),
                done=progress.get(t.id, 0) >= t.target,
            )
            for t in template.tasks
        ]
        done = sum(t.done for t in tasks)
        all_done = done == len(tasks)
        return DailyQuest(
            id=template.id,
            date=doc["date"],
            title=template.title,
            reward_xp=template.reward_xp,
            progress_percent=round(100 * done / len(tasks)) if tasks else 100,
            tasks=tasks,
            claimed=doc.get("claimed", False),
            claimable=all_done and not doc.get("claimed", False),
        )

    async def daily(self, user_id: str) -> DailyQuest:
        return self._view(*await self._load(user_id, today()))

    async def record(self, user_id: str, event: QuestEvent, count: int = 1) -> None:
        day = today()
        _, template = await self._load(user_id, day)
        task_ids = [t.id for t in template.tasks if t.event == event]
        if task_ids:
            await self.quests.increment(user_id, day.isoformat(), task_ids, count)

    async def claim(self, user_id: str) -> QuestClaimResult:
        day = today()
        quest = self._view(*await self._load(user_id, day))
        if quest.claimed:
            raise ConflictError("Today's quest reward was already claimed.")
        if not quest.claimable:
            raise ConflictError("Finish every task first.")
        if not await self.quests.mark_claimed(user_id, day.isoformat()):
            raise ConflictError("Today's quest reward was already claimed.")
        try:
            award = await self.wallet.earn(
                user_id,
                quest.reward_xp,
                f"Daily quest: {quest.title}",
                reward_key=f"quest:{day.isoformat()}",
                activity=f"completed the daily quest {quest.title}",
                sprite="scroll",
            )
        except Exception:
            await self.quests.unmark_claimed(user_id, day.isoformat())
            raise
        return QuestClaimResult(
            quest=quest.model_copy(update={"claimed": True, "claimable": False}),
            awarded=award.awarded,
            balance=award.balance,
        )


class ProgressTracker:
    """The single place game events land: advances daily quests and re-checks achievements."""

    def __init__(self, quests: QuestService, achievements):
        self.quests = quests
        self.achievements = achievements

    async def record(self, user_id: str, event: QuestEvent, count: int = 1) -> None:
        await self.quests.record(user_id, event, count)
        await self.achievements.evaluate(user_id)

    async def refresh_achievements(self, user_id: str) -> None:
        """After stats change outside a quest event."""
        await self.achievements.evaluate(user_id)
