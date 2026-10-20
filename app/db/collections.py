"""Every MongoDB collection the app uses, in one place."""

# Catalog — read-only content, (re)loaded by the seeder.
COURSES = "courses"
COURSE_PATHS = "course_paths"
LESSONS = "lessons"
PROBLEMS = "problems"
SQL_TABLES = "sql_tables"
SQL_PROBLEMS = "sql_problems"
QUEST_TEMPLATES = "quest_templates"
ACHIEVEMENTS = "achievements"
RESUME_TEMPLATES = "resume_templates"
XP_PLANS = "xp_plans"
XP_PACKS = "xp_packs"
STREAK_MILESTONES = "streak_milestones"

CATALOG = (
    COURSES,
    COURSE_PATHS,
    LESSONS,
    PROBLEMS,
    SQL_TABLES,
    SQL_PROBLEMS,
    QUEST_TEMPLATES,
    ACHIEVEMENTS,
    RESUME_TEMPLATES,
    XP_PLANS,
    XP_PACKS,
    STREAK_MILESTONES,
)

# Player state.
USERS = "users"
XP_LEDGER = "xp_ledger"
COURSE_PROGRESS = "course_progress"
CHALLENGE_ATTEMPTS = "challenge_attempts"
DAILY_QUESTS = "daily_quests"
FRIEND_REQUESTS = "friend_requests"
FRIENDSHIPS = "friendships"
DUELS = "duels"
SUBSCRIPTIONS = "subscriptions"
PURCHASES = "purchases"
RESUMES = "resumes"
JOB_APPLICATIONS = "job_applications"
SUBMISSIONS = "submissions"

# Auth.
REFRESH_TOKENS = "refresh_tokens"
LOGIN_FAILURES = "login_failures"

# Caches.
TUTORIAL_CACHE = "tutorial_cache"
EXERCISM_CACHE = "exercism_cache"
# Live job listings, and when each job board feed was last fetched.
JOB_LISTINGS = "job_listings"
JOB_FEEDS = "job_feeds"
