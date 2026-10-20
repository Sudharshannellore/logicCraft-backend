from datetime import UTC, datetime, timedelta

import httpx
import pytest
import respx

from app.domain.jobs import employment_for, languages_in, level_for, location_for, salary_for, tags_for
from app.integrations.jobs.boards import HimalayasBoard, JobBoardUnavailable, JobicyBoard
from app.integrations.jobs.html import html_to_markdown
from app.services import jobs as jobs_module
from app.services.jobs import JobService, feed_due

NOW = datetime(2026, 10, 20, 12, tzinfo=UTC)


# --- Which languages a job asks for -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Senior Python / Django engineer", ["python"]),
        ("JavaScript and TypeScript, Node.js backend", ["javascript", "typescript"]),
        ("Java developer (Spring Boot)", ["java"]),
        ("We use NoSQL stores only", []),
        ("PostgreSQL and MySQL experience", ["sql"]),
        ("C# / .NET developer", ["csharp"]),
        ("Modern C++ (C++20) engineer", ["cpp"]),
        ("Embedded C developer for firmware", ["c"]),
        ("Experience with C/C++ required", ["cpp", "c"]),
        ("Series C startup, C-level reporting", []),
        ("Golang microservices", ["go"]),
        ("Backend services in Go and Rust", ["go", "rust"]),
        ("Go-to-market lead. Go above and beyond!", []),
        ("iOS engineer: Swift and SwiftUI", ["swift"]),
        ("Android with Kotlin", ["kotlin"]),
        ("Laravel / PHP", ["php"]),
    ],
)
def test_languages_are_found_without_false_friends(text, expected):
    assert sorted(languages_in(text)) == sorted(expected)


def test_tags_pick_known_technologies():
    assert tags_for("React + TypeScript frontend on AWS with Docker") == ["TypeScript", "React", "AWS", "Docker"]


# --- Mapping board fields onto ours ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("Full Time", "Full-time"), ("Full-Time", "Full-time"), ("Contractor", "Contract"), ("Part Time", "Part-time"),
     ("Intern", "Internship"), (None, "Full-time"), ("Temporary", "Contract")],
)  # fmt: skip
def test_employment_types(raw, expected):
    assert employment_for(raw) == expected


def test_levels_come_from_the_board_then_the_title():
    assert level_for("Software Engineer", ["Entry-level"], "Full-time") == "Junior"
    assert level_for("Software Engineer", ["Mid-level", "Senior"], "Full-time") == "Mid-level"
    assert level_for("Staff Engineer", [], "Full-time") == "Senior"
    assert level_for("Graduate Developer", [], "Full-time") == "Junior"
    assert level_for("Backend Developer", [], "Full-time") == "Mid-level"
    assert level_for("Software Engineering Intern", ["Senior"], "Full-time") == "Intern"


def test_locations_and_salaries():
    assert location_for([]) == "Remote · Worldwide"
    assert location_for(["Anywhere"]) == "Remote · Worldwide"
    assert location_for(["USA", "Canada"]) == "Remote · USA, Canada"
    assert location_for([f"Country {i}" for i in range(12)]) == "Remote · 12 countries"
    assert salary_for(60000, 85000, "USD", "annual") == "$60k – $85k"
    assert salary_for(60, 120, "USD", "hourly") == "$60 – $120/hr"
    assert salary_for(None, None, "USD", "annual") is None
    assert salary_for(50000, None, "EUR", None) == "€50k"


def test_html_descriptions_become_safe_markdown():
    html = (
        "<h3>About</h3><p>We build <strong>tools</strong> &amp; games.</p>"
        "<ul><li>Write <em>Python</em></li><li>Review code</li></ul>"
        '<p>See <a href="https://example.com/x">our site</a> or <a href="javascript:alert(1)">this</a>.</p>'
        "<script>alert('x')</script><p>Use *stars* and <b></b>[brackets]</p>"
    )
    md = html_to_markdown(html)
    assert "### About" in md
    assert "We build **tools** & games." in md
    assert "- Write *Python*" in md and "- Review code" in md
    assert "[our site](https://example.com/x)" in md
    assert "javascript:" not in md and "alert" not in md
    assert r"\*stars\*" in md and r"\[brackets\]" in md


# --- Board clients ---------------------------------------------------------------------------------------------

HIMALAYAS_JOB = {
    "guid": "https://himalayas.app/companies/acme/jobs/python-dev",
    "applicationLink": "https://himalayas.app/companies/acme/jobs/python-dev?utm_source=api",
    "title": "Junior Python Developer",
    "companyName": "Acme",
    "employmentType": "Full Time",
    "seniority": ["Entry-level"],
    "locationRestrictions": ["Germany"],
    "minSalary": 50000,
    "maxSalary": 65000,
    "currency": "EUR",
    "salaryPeriod": "annual",
    "pubDate": int((NOW - timedelta(days=2)).timestamp()),
    "expiryDate": int((NOW + timedelta(days=30)).timestamp()),
    "excerpt": "Build data tools in Python.",
    "description": "<p>Build data tools in <strong>Python</strong> and SQL.</p>",
}
JOBICY_JOB = {
    "id": 4242,
    "url": "https://jobicy.com/jobs/4242-rust-engineer",
    "jobTitle": "Senior Rust Engineer",
    "companyName": "Ferrous",
    "jobType": ["Contract"],
    "jobLevel": "Any",
    "jobGeo": "Anywhere",
    "pubDate": "2026-10-19T08:00:00+00:00",
    "jobExcerpt": "Systems work in Rust.",
    "jobDescription": "<p>Systems work in Rust.</p>",
}


@respx.mock
async def test_himalayas_jobs_are_normalised():
    route = respx.get(HimalayasBoard.URL).mock(
        side_effect=[httpx.Response(200, json={"jobs": [HIMALAYAS_JOB]}), httpx.Response(200, json={"jobs": []})]
    )
    async with httpx.AsyncClient() as http:
        [job] = await HimalayasBoard(http).search("python")
    assert route.calls[0].request.url.params["q"] == "python"
    assert (job.role, job.company, job.level, job.employment) == (
        "Junior Python Developer",
        "Acme",
        "Junior",
        "Full-time",
    )
    assert job.location == "Remote · Germany" and job.salary == "€50k – €65k"
    assert job.languages == ["python", "sql"] and job.title_languages == ["python"]
    assert job.apply_url.endswith("utm_source=api") and job.source == "Himalayas"
    assert job.id.startswith("himalayas-")


@respx.mock
async def test_jobicy_jobs_are_normalised_and_apply_goes_to_jobicy():
    respx.get(JobicyBoard.URL).mock(return_value=httpx.Response(200, json={"jobs": [JOBICY_JOB]}))
    async with httpx.AsyncClient() as http:
        [job] = await JobicyBoard(http).search("rust")
    assert job.id == "jobicy-4242" and job.level == "Senior" and job.employment == "Contract"
    assert job.location == "Remote · Worldwide" and job.salary is None
    assert job.apply_url == job.source_url == JOBICY_JOB["url"]


@respx.mock
async def test_a_failing_board_raises_unavailable():
    respx.get(JobicyBoard.URL).mock(return_value=httpx.Response(429))
    async with httpx.AsyncClient() as http:
        with pytest.raises(JobBoardUnavailable):
            await JobicyBoard(http).search("python")


# --- Feed refreshes -------------------------------------------------------------------------------------------------


def test_feeds_refresh_every_few_hours_and_retry_failures_sooner():
    assert feed_due(None, NOW)
    assert not feed_due({"ok": True, "fetched_at": NOW - timedelta(hours=2)}, NOW)
    assert feed_due({"ok": True, "fetched_at": NOW - timedelta(hours=9)}, NOW)
    assert not feed_due({"ok": False, "attempted_at": NOW - timedelta(minutes=10)}, NOW)
    assert feed_due({"ok": False, "attempted_at": NOW - timedelta(minutes=31)}, NOW)


class FakeListings:
    def __init__(self):
        self.docs = {}

    async def upsert_many(self, postings, *, keep_until):
        for p in postings:
            doc = p.to_doc()
            old = self.docs.get(doc["_id"], {})
            doc["languages"] = sorted(set(old.get("languages", [])) | set(doc["languages"]))
            doc["expires_at"] = min(p.expires_at, keep_until) if p.expires_at else keep_until
            self.docs[doc["_id"]] = doc

    async def search(self, filters, *, limit):
        out = [
            d
            for d in self.docs.values()
            if d["expires_at"] > filters["expires_at"]["$gt"]
            and ("languages" not in filters or filters["languages"] in d["languages"])
            and all(d[k] == filters[k] for k in ("work_mode", "employment", "level") if k in filters)
        ]
        return sorted(out, key=lambda d: d["posted_at"], reverse=True)[:limit]

    async def get(self, job_id):
        return self.docs.get(job_id)


class FakeFeeds:
    def __init__(self):
        self.states = {}

    async def all(self):
        return dict(self.states)

    async def record(self, key, *, attempted_at, ok, count):
        state = self.states.setdefault(key, {"_id": key})
        state.update(attempted_at=attempted_at, ok=ok)
        if ok:
            state.update(fetched_at=attempted_at, count=count)


class FakeBoard:
    def __init__(self, name, postings=(), fail=False):
        self.name, self.home, self.postings, self.fail, self.calls = name, f"https://{name}.example", postings, fail, 0

    async def search(self, language):
        self.calls += 1
        if self.fail:
            raise JobBoardUnavailable("down")
        return list(self.postings)


@respx.mock
async def test_listings_are_cached_filtered_and_survive_a_board_outage(monkeypatch):
    monkeypatch.setattr(jobs_module, "utcnow", lambda: NOW)
    respx.get(HimalayasBoard.URL).mock(
        side_effect=[httpx.Response(200, json={"jobs": [HIMALAYAS_JOB]}), httpx.Response(200, json={"jobs": []})]
    )
    async with httpx.AsyncClient() as http:
        postings = await HimalayasBoard(http).search("python")
    good = FakeBoard("Himalayas", postings)
    down = FakeBoard("Jobicy", fail=True)
    service = JobService([good, down], FakeListings(), FakeFeeds(), None, None, None)

    listed = await service.list_jobs(language="python", work_mode=None, employment=None, level=None, search=None)
    assert [j.role for j in listed.jobs] == ["Junior Python Developer"]
    assert listed.stale and [s.name for s in listed.sources] == ["Himalayas", "Jobicy"]
    assert listed.jobs[0].posted_days_ago == 2

    # Cached: the healthy board isn't asked again for hours; the failed one waits before retrying.
    await service.list_jobs(language="python", work_mode=None, employment=None, level=None, search=None)
    assert (good.calls, down.calls) == (1, 1)

    sql = await service.list_jobs(language="sql", work_mode=None, employment=None, level=None, search=None)
    assert len(sql.jobs) == 1  # the same job also asks for SQL
    none = await service.list_jobs(language="python", work_mode=None, employment=None, level="Senior", search=None)
    assert none.jobs == []
    searched = await service.list_jobs(language="python", work_mode=None, employment=None, level=None, search="acme")
    assert len(searched.jobs) == 1
