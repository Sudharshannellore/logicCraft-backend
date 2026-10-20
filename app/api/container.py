"""Composition root: builds repositories and services for one request, lazily.

Only what a route actually touches gets constructed. Long-lived resources (Mongo client, HTTP
client, code executor, tutorial providers) are created once in the app lifespan and shared.
"""

from functools import cached_property

import httpx
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import Settings
from app.integrations.execution import CodeExecutor
from app.integrations.exercism.client import ExercismClient
from app.integrations.jobs.boards import build_boards
from app.integrations.tutorials import TutorialProvider
from app.repositories import catalog
from app.repositories.auth import LoginFailureRepository, RefreshTokenRepository
from app.repositories.challenges import ChallengeAttemptRepository
from app.repositories.exercism_cache import ExercismCacheRepository
from app.repositories.jobs import JobFeedRepository, JobListingRepository
from app.repositories.ledger import LedgerRepository
from app.repositories.player_content import (
    JobApplicationRepository,
    PurchaseRepository,
    ResumeRepository,
    SubmissionRepository,
    SubscriptionRepository,
)
from app.repositories.progress import CourseProgressRepository, DailyQuestRepository
from app.repositories.social import DuelRepository, FriendRequestRepository, FriendshipRepository
from app.repositories.tutorial_cache import TutorialCacheRepository
from app.repositories.users import UserRepository
from app.services.achievements import AchievementService
from app.services.auth import AuthService
from app.services.challenges import ChallengeService
from app.services.jobs import JobService, ResumeAIService
from app.services.leaderboard import LeaderboardService
from app.services.learning import LearningService
from app.services.library import LibraryService
from app.services.mentor import MentorService
from app.services.practice import PracticeService
from app.services.quests import ProgressTracker, QuestService
from app.services.resumes import ResumeService
from app.services.rewards import RewardService
from app.services.social import DuelService, SocialService
from app.services.sql import SqlService
from app.services.store import StoreService
from app.services.tutorials import TutorialService
from app.services.users import UserService
from app.services.wallet import WalletService


class Container:
    def __init__(
        self,
        *,
        db: AsyncDatabase,
        settings: Settings,
        http: httpx.AsyncClient,
        executor: CodeExecutor,
        providers: list[TutorialProvider],
    ):
        self.db = db
        self.settings = settings
        self.http = http
        self.executor = executor
        self.providers = providers

    # --- Repositories ---------------------------------------------------------------------

    @cached_property
    def user_repo(self) -> UserRepository:
        return UserRepository(self.db)

    @cached_property
    def ledger_repo(self) -> LedgerRepository:
        return LedgerRepository(self.db)

    @cached_property
    def friendship_repo(self) -> FriendshipRepository:
        return FriendshipRepository(self.db)

    @cached_property
    def problem_repo(self) -> catalog.ProblemRepository:
        return catalog.ProblemRepository(self.db)

    @cached_property
    def lesson_repo(self) -> catalog.LessonRepository:
        return catalog.LessonRepository(self.db)

    @cached_property
    def submission_repo(self) -> SubmissionRepository:
        return SubmissionRepository(self.db)

    @cached_property
    def resume_repo(self) -> ResumeRepository:
        return ResumeRepository(self.db)

    # --- Core services ------------------------------------------------------------------------

    @cached_property
    def wallet(self) -> WalletService:
        return WalletService(self.user_repo, self.ledger_repo)

    @cached_property
    def users(self) -> UserService:
        return UserService(self.user_repo)

    @cached_property
    def auth(self) -> AuthService:
        return AuthService(
            self.user_repo, RefreshTokenRepository(self.db), LoginFailureRepository(self.db), self.users, self.settings
        )

    @cached_property
    def achievements(self) -> AchievementService:
        return AchievementService(catalog.AchievementRepository(self.db), self.user_repo)

    @cached_property
    def quests(self) -> QuestService:
        return QuestService(catalog.QuestTemplateRepository(self.db), DailyQuestRepository(self.db), self.wallet)

    @cached_property
    def tracker(self) -> ProgressTracker:
        return ProgressTracker(self.quests, self.achievements)

    @cached_property
    def rewards(self) -> RewardService:
        return RewardService(catalog.StreakMilestoneRepository(self.db), self.user_repo, self.wallet)

    # --- Learning --------------------------------------------------------------------------------

    @cached_property
    def exercism_cache(self) -> ExercismCacheRepository:
        return ExercismCacheRepository(self.db)

    @cached_property
    def exercism(self) -> ExercismClient:
        return ExercismClient(self.http, self.exercism_cache)

    @cached_property
    def library(self) -> LibraryService:
        return LibraryService(
            self.exercism,
            self.executor,
            self.submission_repo,
            self.user_repo,
            self.wallet,
            self.tracker,
            self.settings,
        )

    @cached_property
    def tutorials(self) -> TutorialService:
        return TutorialService(
            self.providers, TutorialCacheRepository(self.db), timeout_seconds=self.settings.http_timeout_seconds
        )

    @cached_property
    def learning(self) -> LearningService:
        return LearningService(
            catalog.CourseRepository(self.db),
            catalog.CoursePathRepository(self.db),
            self.lesson_repo,
            CourseProgressRepository(self.db),
            self.user_repo,
            self.wallet,
            self.tracker,
            self.tutorials,
        )

    @cached_property
    def mentor(self) -> MentorService:
        return MentorService(self.problem_repo, self.learning, self.wallet)

    # --- Practice & challenges ------------------------------------------------------------------

    @cached_property
    def duels(self) -> DuelService:
        return DuelService(
            DuelRepository(self.db), self.user_repo, self.friendship_repo, self.problem_repo, self.wallet, self.tracker
        )

    @cached_property
    def practice(self) -> PracticeService:
        return PracticeService(
            self.problem_repo,
            self.submission_repo,
            self.user_repo,
            self.executor,
            self.wallet,
            self.tracker,
            self.duels,
        )

    @cached_property
    def sql(self) -> SqlService:
        return SqlService(
            catalog.SqlTableRepository(self.db),
            catalog.SqlProblemRepository(self.db),
            self.submission_repo,
            self.user_repo,
            self.wallet,
            self.tracker,
        )

    @cached_property
    def challenges(self) -> ChallengeService:
        return ChallengeService(
            self.exercism,
            self.exercism_cache,
            self.library,
            self.learning,
            ChallengeAttemptRepository(self.db),
            self.user_repo,
            self.wallet,
            self.tracker,
        )

    @cached_property
    def leaderboard(self) -> LeaderboardService:
        return LeaderboardService(self.user_repo, self.ledger_repo, self.friendship_repo)

    # --- Social -----------------------------------------------------------------------------------

    @cached_property
    def social(self) -> SocialService:
        return SocialService(self.user_repo, FriendRequestRepository(self.db), self.friendship_repo)

    # --- Economy & career ---------------------------------------------------------------------------

    @cached_property
    def store(self) -> StoreService:
        return StoreService(
            catalog.XpPlanRepository(self.db),
            catalog.XpPackRepository(self.db),
            SubscriptionRepository(self.db),
            PurchaseRepository(self.db),
            self.wallet,
        )

    @cached_property
    def resumes(self) -> ResumeService:
        return ResumeService(self.resume_repo, catalog.ResumeTemplateRepository(self.db), self.user_repo, self.wallet)

    @cached_property
    def jobs(self) -> JobService:
        return JobService(
            build_boards(self.http),
            JobListingRepository(self.db),
            JobFeedRepository(self.db),
            JobApplicationRepository(self.db),
            self.resume_repo,
            self.wallet,
        )

    @cached_property
    def resume_ai(self) -> ResumeAIService:
        return ResumeAIService(self.users, self.jobs, self.wallet)
