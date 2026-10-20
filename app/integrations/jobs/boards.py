"""Free remote-job boards with public APIs: Himalayas and Jobicy.

Neither is open source, but both publish free, keyless job feeds for other sites to show, on three
conditions this app follows: credit the board with a visible link, send every Apply click to the board's
own link, and don't pass the listings on to other job boards. Both refresh about daily and ask callers to
cache, so listings are stored in MongoDB and each language's feed is fetched at most every few hours.

- Himalayas: https://himalayas.app/api (search, about 20 jobs a page)
- Jobicy: https://jobicy.com/jobs-rss-feed (tag search; jobs from the last 7 days)
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import httpx

from app.domain.jobs import (
    SEARCH_TERMS,
    employment_for,
    languages_in,
    level_for,
    location_for,
    logo_for,
    salary_for,
    tags_for,
)
from app.integrations.jobs.html import html_to_markdown, html_to_text

logger = logging.getLogger(__name__)

SUMMARY_CHARS = 280


class JobBoardUnavailable(Exception):
    """The board couldn't be reached, refused the request, or answered with something unexpected."""


@dataclass
class JobPosting:
    id: str
    source: str
    company: str
    role: str
    location: str
    work_mode: str
    employment: str
    level: str
    salary: str | None
    posted_at: datetime
    expires_at: datetime | None
    summary: str
    description: str
    tags: list[str]
    languages: list[str]
    # Languages named in the job title — those listings rank first.
    title_languages: list[str]
    source_url: str
    apply_url: str
    logo_sprite: str = field(default="briefcase")
    logo_color: str = field(default="#a78bfa")

    def to_doc(self) -> dict[str, Any]:
        doc = dict(self.__dict__)
        doc["_id"] = doc.pop("id")
        return doc


def _summary(excerpt: str | None, text: str) -> str:
    base = html_to_text(excerpt) if excerpt else text
    return base if len(base) <= SUMMARY_CHARS else base[:SUMMARY_CHARS].rsplit(" ", 1)[0] + "…"


def _posting(
    *,
    id: str,
    source: str,
    company: str,
    role: str,
    places: list[str],
    raw_employment: str | None,
    board_levels: list[str],
    salary: str | None,
    posted_at: datetime,
    expires_at: datetime | None,
    excerpt: str | None,
    html: str,
    source_url: str,
    apply_url: str,
) -> JobPosting:
    text = html_to_text(html)
    employment = employment_for(raw_employment)
    sprite, color = logo_for(company)
    return JobPosting(
        id=id,
        source=source,
        company=company.strip() or "Unnamed company",
        role=role.strip(),
        location=location_for(places),
        work_mode="Remote",  # both boards list remote jobs only
        employment=employment,
        level=level_for(role, board_levels, employment),
        salary=salary,
        posted_at=posted_at,
        expires_at=expires_at,
        summary=_summary(excerpt, text),
        description=html_to_markdown(html),
        tags=tags_for(f"{role}\n{text}"),
        languages=languages_in(f"{role}\n{text}"),
        title_languages=languages_in(role),
        source_url=source_url,
        apply_url=apply_url,
        logo_sprite=sprite,
        logo_color=color,
    )


async def _get_json(http: httpx.AsyncClient, url: str, params: dict[str, Any]) -> Any:
    try:
        response = await http.get(url, params=params, timeout=15.0)
    except httpx.HTTPError as exc:
        raise JobBoardUnavailable(f"{type(exc).__name__} for {url}") from exc
    if response.status_code != 200:
        raise JobBoardUnavailable(f"{url} answered {response.status_code}")
    try:
        return response.json()
    except ValueError as exc:
        raise JobBoardUnavailable(f"{url} sent invalid JSON") from exc


def _epoch(value: Any) -> datetime | None:
    try:
        return datetime.fromtimestamp(int(value), UTC) if value else None
    except (TypeError, ValueError, OSError):
        return None


def _iso(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


class HimalayasBoard:
    name = "Himalayas"
    home = "https://himalayas.app/jobs"
    URL = "https://himalayas.app/jobs/api/search"
    PAGES = 2

    def __init__(self, http: httpx.AsyncClient):
        self.http = http

    def _parse(self, raw: dict[str, Any]) -> JobPosting | None:
        guid, link, title = raw.get("guid"), raw.get("applicationLink"), raw.get("title")
        posted = _epoch(raw.get("pubDate"))
        if not (guid and link and title and posted):
            return None
        return _posting(
            id="himalayas-" + hashlib.sha256(str(guid).encode()).hexdigest()[:16],
            source=self.name,
            company=raw.get("companyName") or "",
            role=title,
            places=list(raw.get("locationRestrictions") or []),
            raw_employment=raw.get("employmentType"),
            board_levels=list(raw.get("seniority") or []),
            salary=salary_for(raw.get("minSalary"), raw.get("maxSalary"), raw.get("currency"), raw.get("salaryPeriod")),
            posted_at=posted,
            expires_at=_epoch(raw.get("expiryDate")),
            excerpt=raw.get("excerpt"),
            html=raw.get("description") or raw.get("excerpt") or "",
            source_url=str(guid),
            apply_url=str(link),
        )

    async def search(self, language: str) -> list[JobPosting]:
        term = SEARCH_TERMS[language]["himalayas"]
        found: dict[str, JobPosting] = {}
        for page in range(1, self.PAGES + 1):
            data = await _get_json(self.http, self.URL, {"q": term, "page": page, "sort": "recent"})
            raw_jobs = data.get("jobs") if isinstance(data, dict) else None
            if not raw_jobs:
                break
            for raw in raw_jobs:
                posting = self._parse(raw)
                if posting:
                    found[posting.id] = posting
        return list(found.values())


class JobicyBoard:
    name = "Jobicy"
    home = "https://jobicy.com"
    URL = "https://jobicy.com/api/v2/remote-jobs"

    def __init__(self, http: httpx.AsyncClient):
        self.http = http

    def _parse(self, raw: dict[str, Any]) -> JobPosting | None:
        url, title, posted = raw.get("url"), raw.get("jobTitle"), _iso(raw.get("pubDate"))
        if not (url and title and posted and raw.get("id")):
            return None
        geo = str(raw.get("jobGeo") or "")
        types = raw.get("jobType") or []
        level = raw.get("jobLevel") or ""
        return _posting(
            id=f"jobicy-{raw['id']}",
            source=self.name,
            company=raw.get("companyName") or "",
            role=title,
            places=[p for p in (s.strip() for s in geo.split(",")) if p],
            raw_employment=" ".join(types) if isinstance(types, list) else str(types),
            board_levels=[] if level.lower() == "any" else [level],
            salary=salary_for(
                raw.get("annualSalaryMin") or raw.get("salaryMin"),
                raw.get("annualSalaryMax") or raw.get("salaryMax"),
                raw.get("salaryCurrency"),
                raw.get("salaryPeriod") or ("annual" if raw.get("annualSalaryMin") else None),
            ),
            posted_at=posted,
            expires_at=None,
            excerpt=raw.get("jobExcerpt"),
            html=raw.get("jobDescription") or raw.get("jobExcerpt") or "",
            # Jobicy asks that Apply goes to the listing on Jobicy.
            source_url=str(url),
            apply_url=str(url),
        )

    async def search(self, language: str) -> list[JobPosting]:
        term = SEARCH_TERMS[language]["jobicy"]
        data = await _get_json(self.http, self.URL, {"count": 50, "tag": term})
        raw_jobs = data.get("jobs") if isinstance(data, dict) else None
        if raw_jobs is None:
            raise JobBoardUnavailable("Jobicy sent no job list")
        return [p for p in (self._parse(r) for r in raw_jobs) if p]


JobBoard = HimalayasBoard | JobicyBoard


def build_boards(http: httpx.AsyncClient) -> list[JobBoard]:
    return [HimalayasBoard(http), JobicyBoard(http)]
