"""Quest AI resume assistant (ported from the frontend's resumeAi.ts).

Rule-based stand-in for a model. It never invents numbers — missing metrics become
[bracketed placeholders] for the learner to fill in.
"""

import re
from dataclasses import dataclass

from app.schemas.resumes import JobMatch, ResumeData, TailorResult


@dataclass(frozen=True)
class LearnerFacts:
    """What Quest AI may cite about the learner — taken from their real Logicraft profile."""

    problems_solved: int
    accuracy: int
    rank: int
    league_label: str
    longest_streak: int


WEAK_OPENERS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^(worked on|working on)\s+", re.I), "Built "),
    (re.compile(r"^(fixed|fixing)\s+", re.I), "Resolved "),
    (re.compile(r"^(helped|helping)( with)?\s+", re.I), "Collaborated on "),
    (re.compile(r"^(made|making)\s+", re.I), "Developed "),
    (re.compile(r"^(did|doing)\s+", re.I), "Delivered "),
    (re.compile(r"^(was responsible for|responsible for)\s+", re.I), "Owned "),
    (re.compile(r"^(used|using)\s+", re.I), "Leveraged "),
    (re.compile(r"^(solved)\s+", re.I), "Solved "),
    (re.compile(r"^(wrote|writing)\s+", re.I), "Authored "),
]

# Skills evidenced by cleared Logicraft topics.
EARNED_SKILLS = ["Data Structures", "Algorithms", "Hash Tables", "Recursion", "Problem Solving", "SQL Joins", "Git"]

KNOWN_KEYWORDS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "SQL", "PostgreSQL", "MySQL", "Java", "C++", "Go",
    "REST", "API", "GraphQL", "AWS", "Docker", "Kubernetes", "Git", "CI/CD", "Testing", "Agile", "Algorithms",
    "Data Structures", "Machine Learning", "HTML", "CSS", "Linux", "Microservices", "C#", "PHP", "Rust", "Kotlin",
    "Swift",
]  # fmt: skip


def improve_bullet(text: str) -> str:
    out = text.strip().removesuffix(".")
    if not out:
        return out
    for pattern, replacement in WEAK_OPENERS:
        if pattern.search(out):
            out = pattern.sub(replacement, out, count=1)
            break
    out = out[0].upper() + out[1:]
    if not re.search(r"\d", out):
        out += ", resulting in [measurable impact — e.g. 30% faster load times]"
    return out + "."


def _join(items: list[str], fallback: str) -> str:
    if not items:
        return fallback
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


def generate_summary(data: ResumeData, facts: LearnerFacts) -> str:
    skill_text = _join(data.skills[:3], "modern programming")
    return (
        f"{data.headline or 'Software developer'} skilled in {skill_text}, with {facts.problems_solved} algorithm and SQL "
        f"problems solved at {facts.accuracy}% accuracy. Ranked #{facts.rank} globally ({facts.league_label} league) and "
        "focused on clean, efficient code — from O(n) solutions to well-structured features. Eager to bring strong "
        "problem-solving and fast learning to a product engineering team."
    )


def suggest_skills(existing: list[str]) -> list[str]:
    have = {s.lower() for s in existing}
    return [s for s in EARNED_SKILLS if s.lower() not in have]


def _mentions(text: str, keyword: str) -> bool:
    return re.search(rf"(^|[^a-z0-9]){re.escape(keyword.lower())}([^a-z0-9]|$)", text) is not None


def _resume_text(data: ResumeData) -> str:
    parts = [data.headline, data.summary, " ".join(data.skills)]
    for entry in [*data.experience, *data.projects]:
        parts += [entry.title, entry.subtitle, *entry.bullets]
    return " ".join(parts).lower()


def match_job(data: ResumeData, job_description: str) -> JobMatch:
    job = job_description.lower()
    text = _resume_text(data)
    wanted = [k for k in KNOWN_KEYWORDS if _mentions(job, k)]
    matched = [k for k in wanted if _mentions(text, k)]
    missing = [k for k in wanted if k not in matched]
    score = round(len(matched) / len(wanted) * 100) if wanted else 0
    return JobMatch(score=score, matched=matched, missing=missing)


def tailor_to_job(
    data: ResumeData, job_description: str, facts: LearnerFacts, target: tuple[str, str] | None = None
) -> TailorResult:
    match = match_job(data, job_description)
    focus = match.matched[:4]
    focus_text = (
        f"hands-on experience with {', '.join(focus)}" if focus else "a strong foundation in programming fundamentals"
    )
    closer = (
        f"Excited to bring that to the {target[0]} role at {target[1]}."
        if target
        else "Known for turning requirements into clean, tested code and learning new tools quickly."
    )
    summary = (
        f"{data.headline or 'Software developer'} with {focus_text}, backed by {facts.problems_solved} solved coding "
        f"challenges and a {facts.longest_streak}-day practice streak. {closer}"
    )
    return TailorResult(**match.model_dump(), summary=summary)


def apply_tailoring(data: ResumeData, result: TailorResult) -> ResumeData:
    """The job-specific summary, and the skills the job asks for listed first. Nothing is added."""

    def relevant(skill: str) -> bool:
        return any(_mentions(skill.lower(), k) for k in result.matched)

    skills = [s for s in data.skills if relevant(s)] + [s for s in data.skills if not relevant(s)]
    return data.model_copy(update={"summary": result.summary, "skills": skills})


def write_cover_note(data: ResumeData, role: str, company: str, job_description: str, facts: LearnerFacts) -> str:
    """Short cover note. Anything only the applicant knows is left as a [placeholder]."""
    matched = match_job(data, job_description).matched
    strength_text = _join((matched or data.skills)[:3], "core programming")
    recent = next((e for e in [*data.experience, *data.projects] if e.title.strip()), None)
    recent_line = (
        f"Most recently, as {recent.title}{f' ({recent.subtitle})' if recent.subtitle else ''}, "
        "I [one result you're proud of from this role or project]."
        if recent
        else "[One result you're proud of from a recent project.]"
    )
    return "\n\n".join(
        [
            f"Dear {company} hiring team,",
            f"I'm applying for the {role} position. I'm a {(data.headline or 'software developer').lower()} with hands-on "
            f"experience in {strength_text}, and I've solved {facts.problems_solved} coding and SQL problems on Logicraft "
            f"at {facts.accuracy}% accuracy.",
            recent_line,
            f"What draws me to {company} is [one specific reason — the product, the team, or the problem you want to work "
            "on]. I'd love to talk about how I can help.",
            f"Best regards,\n{data.name or '[Your name]'}",
        ]
    )
