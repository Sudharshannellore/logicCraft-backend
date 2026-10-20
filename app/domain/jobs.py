"""Rules for live job listings: which of the 13 course languages a job uses, and how board fields map onto ours.

Job boards describe the same things in different words ("Full Time", "Full-Time", "Contractor"…). These
helpers turn them into the Job Board's few categories, and find the languages a job asks for so learners
can browse jobs by the language they're studying.
"""

import hashlib
import re
from datetime import datetime

from app.domain.resume_ai import KNOWN_KEYWORDS

# What each board's search is asked for, per course language. Jobicy rejects terms shorter than three
# characters and "#", so it gets its own spelling where needed.
SEARCH_TERMS: dict[str, dict[str, str]] = {
    "python": {"himalayas": "python", "jobicy": "python"},
    "javascript": {"himalayas": "javascript", "jobicy": "javascript"},
    "sql": {"himalayas": "sql", "jobicy": "sql"},
    "typescript": {"himalayas": "typescript", "jobicy": "typescript"},
    "java": {"himalayas": "java", "jobicy": "java"},
    "csharp": {"himalayas": "c#", "jobicy": ".net"},
    "cpp": {"himalayas": "c++", "jobicy": "c++"},
    "c": {"himalayas": "c programming", "jobicy": "c programming"},
    "php": {"himalayas": "php", "jobicy": "php"},
    "go": {"himalayas": "golang", "jobicy": "golang"},
    "rust": {"himalayas": "rust", "jobicy": "rust"},
    "kotlin": {"himalayas": "kotlin", "jobicy": "kotlin"},
    "swift": {"himalayas": "swift", "jobicy": "swift"},
}

_I = re.IGNORECASE
# Board searches are fuzzy, so every job is checked here before it's listed under a language.
# Short names ("C", "Go", "Swift", "Rust") are matched case-sensitively and only in programming contexts.
LANGUAGE_PATTERNS: dict[str, re.Pattern[str]] = {
    "python": re.compile(r"\bPython\b", _I),
    "javascript": re.compile(r"\bJavaScript\b|\bNode\.?js\b", _I),
    "sql": re.compile(r"\b(?:T-|Postgre|My)?SQL\b|\bSQLite\b", _I),
    "typescript": re.compile(r"\bTypeScript\b", _I),
    "java": re.compile(r"\bJava\b(?!\s*Script)", _I),
    "csharp": re.compile(r"C#|(?<![\w.])\.NET\b|\bASP\.NET\b", _I),
    "cpp": re.compile(r"C\+\+"),
    "c": re.compile(
        r"\bC/C\+\+|\bC,\s*C\+\+|\bC and C\+\+|\b[Ee]mbedded C\b|\bANSI C\b|\bC(?:89|99|11|17)\b"
        r"|\bC (?:programming|language|developer|engineer|software)\b|\b(?:in|and|or) C(?=[\s,.;)])(?![#+])"
    ),
    "go": re.compile(
        r"\bGolang\b|\bGo (?:developer|engineer|programming|language|backend|services|microservices)\b"
        r"|\b(?:in|and|or) Go\b(?![-'])|\bGo(?=[,/)])|(?<=[/(])Go\b",
    ),
    "php": re.compile(r"\bPHP\b", _I),
    "rust": re.compile(r"\bRust\b"),
    "kotlin": re.compile(r"\bKotlin\b", _I),
    "swift": re.compile(r"\bSwift(?:UI)?\b"),
}


def languages_in(text: str) -> list[str]:
    """Course language ids the text asks for, in catalog order."""
    return [lang for lang, pattern in LANGUAGE_PATTERNS.items() if pattern.search(text)]


# Extra keywords worth showing as tags (on top of the resume matcher's list).
_TAG_KEYWORDS = [*KNOWN_KEYWORDS, "C#", "PHP", "Rust", "Kotlin", "Swift", "Django", "Flask", "Spring", "Angular",
                 "Vue", "Next.js", ".NET", "Azure", "GCP", "Terraform", "iOS", "Android", "MongoDB", "Redis"]  # fmt: skip


def tags_for(text: str, limit: int = 10) -> list[str]:
    lowered = text.lower()
    found = []
    for keyword in dict.fromkeys(_TAG_KEYWORDS):
        if keyword in ("Go", "API", "Testing", "Agile", "Git"):  # too generic to be useful as a tag
            continue
        if re.search(rf"(^|[^a-z0-9#+]){re.escape(keyword.lower())}([^a-z0-9#+]|$)", lowered):
            found.append(keyword)
    return found[:limit]


# --- Categories -----------------------------------------------------------------------------------------


def employment_for(raw: str | None) -> str:
    value = (raw or "").lower()
    if "intern" in value:
        return "Internship"
    if "part" in value:
        return "Part-time"
    if any(word in value for word in ("contract", "freelance", "temporary", "temp")):
        return "Contract"
    return "Full-time"


_SENIOR = re.compile(r"\b(?:senior|sr\.?|lead|principal|staff|head|director|architect|manager|vp)\b", _I)
_JUNIOR = re.compile(r"\b(?:junior|jr\.?|entry|graduate|grad|trainee|apprentice|associate)\b", _I)
_INTERN = re.compile(r"\bintern(?:ship)?\b", _I)


def level_for(title: str, board_levels: list[str], employment: str) -> str:
    """Intern, Junior, Mid-level or Senior: the board's own level when it gives one, else the job title."""
    if employment == "Internship" or _INTERN.search(title):
        return "Intern"
    joined = " ".join(board_levels).lower()
    if "entry" in joined or "junior" in joined:
        return "Junior"
    if "mid" in joined:
        return "Mid-level"
    if any(word in joined for word in ("senior", "director", "manager", "executive", "lead")):
        return "Senior"
    if _SENIOR.search(title):
        return "Senior"
    if _JUNIOR.search(title):
        return "Junior"
    return "Mid-level"


def location_for(places: list[str]) -> str:
    places = [p.strip() for p in places if p and p.strip()]
    if not places or any(p.lower() in ("anywhere", "worldwide", "global") for p in places):
        return "Remote · Worldwide"
    if len(places) <= 3:
        return f"Remote · {', '.join(places)}"
    return f"Remote · {len(places)} countries"


_CURRENCY = {"USD": "$", "EUR": "€", "GBP": "£", "CAD": "CA$", "AUD": "A$", "INR": "₹"}


def salary_for(low: float | None, high: float | None, currency: str | None, period: str | None) -> str | None:
    """'$60k – $85k', '$40 – $60/hr' or None when the board doesn't say."""
    values = [v for v in (low, high) if v]
    if not values:
        return None
    symbol = _CURRENCY.get((currency or "USD").upper(), f"{(currency or '').upper()} ")
    hourly = (period or "").lower() in ("hourly", "hour")

    def fmt(v: float) -> str:
        return f"{symbol}{round(v)}" if hourly or v < 1000 else f"{symbol}{round(v / 1000)}k"

    text = fmt(values[0]) if len(values) == 1 or values[0] == values[-1] else f"{fmt(values[0])} – {fmt(values[-1])}"
    if hourly:
        return f"{text}/hr"
    if (period or "").lower() in ("monthly", "month"):
        return f"{text}/mo"
    return text


_LOGO_SPRITES = (
    "briefcase",
    "terminal",
    "database",
    "gear",
    "castle",
    "gem",
    "compass",
    "scroll",
    "floppy",
    "lightning",
)
_LOGO_COLORS = ("#a78bfa", "#4ade80", "#38bdf8", "#f472b6", "#fb923c", "#facc15", "#2dd4bf", "#f87171")


def logo_for(company: str) -> tuple[str, str]:
    """A stable pixel 'logo' (sprite and colour) per company — board logos are their trademarks."""
    digest = int(hashlib.sha256(company.lower().encode()).hexdigest(), 16)
    return _LOGO_SPRITES[digest % len(_LOGO_SPRITES)], _LOGO_COLORS[digest // 16 % len(_LOGO_COLORS)]


def days_ago(posted_at: datetime, now: datetime) -> int:
    return max(0, (now - posted_at).days)
