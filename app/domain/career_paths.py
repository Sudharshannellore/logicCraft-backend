"""Career paths: the industry routes learners can take, as ordered lists of courses. No I/O.

A path is only a recipe over courses, not content. A language is usually the first step and frameworks
follow (Python → FastAPI, JavaScript → React → Next.js). Courses come from the live course catalog, so a
step whose course can't be loaded right now is simply left out. Steps are suggestions in order, never locks:
learners may take any step first, and what they've finished already shows as completed.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

StepState = Literal["completed", "in_progress", "next", "available"]


@dataclass(frozen=True)
class CareerPath:
    id: str
    title: str
    tagline: str
    description: str
    sprite: str
    steps: tuple[str, ...]  # course ids, in the order to take them


PATHS: tuple[CareerPath, ...] = (
    CareerPath(
        "full-stack-web",
        "Full-Stack Web Developer",
        "Build and ship complete web apps.",
        "Learn the language of the web, add types, build interfaces with React, go full-stack with Next.js "
        "and store your data in SQL.",
        "terminal",
        ("live-javascript", "live-typescript", "fw-react", "fw-nextjs", "live-sql"),
    ),
    CareerPath(
        "frontend",
        "Frontend Engineer",
        "Craft fast, accessible interfaces.",
        "Master JavaScript and TypeScript, then the component frameworks teams hire for: React, Svelte and Next.js.",
        "star",
        ("live-javascript", "live-typescript", "fw-react", "fw-svelte", "fw-nextjs"),
    ),
    CareerPath(
        "backend-node",
        "Backend Engineer (Node.js)",
        "Servers and APIs in JavaScript.",
        "Learn JavaScript and TypeScript, build servers with Express, and keep data in SQL.",
        "database",
        ("live-javascript", "live-typescript", "fw-express", "live-sql"),
    ),
    CareerPath(
        "backend-python",
        "Backend Engineer (Python)",
        "Fast, typed APIs backed by SQL.",
        "Start with Python and SQL, then build production-style APIs with FastAPI.",
        "database",
        ("live-python", "live-sql", "fw-fastapi"),
    ),
    CareerPath(
        "backend-php",
        "Web Developer (PHP)",
        "Ship web apps with Laravel.",
        "Learn PHP and SQL, then build full applications with Laravel's routing, controllers and Eloquent.",
        "compass",
        ("live-php", "live-sql", "fw-laravel"),
    ),
    CareerPath(
        "ai-ml",
        "AI / Machine Learning Engineer",
        "From classical ML to LLM apps.",
        "Learn Python, classical machine learning with scikit-learn, pretrained transformers with Hugging Face, "
        "and build applications on large language models.",
        "lightning",
        ("live-python", "fw-scikit-learn", "fw-huggingface", "fw-generative-ai"),
    ),
    CareerPath(
        "data-science",
        "Data Analyst / Data Scientist",
        "Turn data into decisions.",
        "Query data with SQL, analyse it with Python, and learn the full data science workflow.",
        "treasureMap",
        ("live-sql", "live-python", "fw-data-science"),
    ),
    CareerPath(
        "systems",
        "Systems Programmer",
        "Close to the machine, built to last.",
        "Learn C for how computers work, C++ and Rust for performance and safety, and Go for modern infrastructure.",
        "sword",
        ("live-c", "live-cpp", "live-rust", "live-go"),
    ),
    CareerPath(
        "enterprise",
        "Enterprise Application Developer",
        "The languages big companies run on.",
        "Learn Java, C# and Kotlin for large-scale applications, plus the SQL behind them.",
        "trophy",
        ("live-java", "live-csharp", "live-kotlin", "live-sql"),
    ),
    CareerPath(
        "mobile",
        "Mobile App Developer",
        "Apps for Android and iPhone.",
        "Learn Kotlin for Android and Swift for iOS.",
        "scroll",
        ("live-kotlin", "live-swift"),
    ),
)

PATHS_BY_ID = {p.id: p for p in PATHS}


def step_states(percents: Sequence[int]) -> list[StepState]:
    """Per step, given each course's progress: finished, underway, the one to take next, or just available."""
    first_open = next((i for i, p in enumerate(percents) if p < 100), None)
    states: list[StepState] = []
    for i, percent in enumerate(percents):
        if percent >= 100:
            states.append("completed")
        elif percent > 0:
            states.append("in_progress")
        else:
            states.append("next" if i == first_open else "available")
    return states


def path_progress(percents: Sequence[int]) -> tuple[int, int]:
    """(courses finished, overall percent)."""
    if not percents:
        return 0, 0
    return sum(1 for p in percents if p >= 100), round(sum(min(p, 100) for p in percents) / len(percents))


def reason_to_recommend(titles: Sequence[str], percents: Sequence[int]) -> str | None:
    """Why this path suits the learner, from what they've already done in it; None if it isn't relevant yet."""
    if percents and all(p >= 100 for p in percents):
        return None
    finished = [t for t, p in zip(titles, percents, strict=True) if p >= 100]
    started = [t for t, p in zip(titles, percents, strict=True) if 0 < p < 100]
    if finished:
        return "You finished " + _list(finished)
    if started:
        return "You're learning " + _list(started)
    return None


def _list(names: Sequence[str]) -> str:
    shown = list(names[:2])
    text = " and ".join(shown)
    return text + (f" and {len(names) - 2} more" if len(names) > 2 else "")
