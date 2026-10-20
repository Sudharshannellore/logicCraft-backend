"""XP prices and payouts. The frontend reads them from GET /config/economy instead of hard-coding them."""

# Spendable XP a new player starts with, so Quest AI and a first template are reachable on day one.
STARTER_XP = 200

AI_ANSWER_COST = 10

RESUME_AI_COST = {
    "summary": 30,
    "bullet": 10,
    "skills": 15,
    "tailor": 50,
    "cover_note": 25,
}

FREE_RESUME_SLOTS = 1
RESUME_SLOT_COST = 100
MAX_RESUMES = 8

DUEL_WIN_BONUS = 40
DUEL_STAKES = (0, 25, 50, 100)
DUEL_TIME_LIMITS = (10, 20, 30)

# An accepted duel the player never opens is scored as "out of time" after this long.
DUEL_START_GRACE_HOURS = 24
