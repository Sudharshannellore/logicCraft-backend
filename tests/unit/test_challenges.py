from datetime import UTC, datetime, timedelta

import pytest

from app.core.errors import ConflictError, NotFoundError
from app.domain.challenges import (
    Candidate,
    challenge_id,
    parse_id,
    period_bounds,
    period_of,
    pick_boss,
    shortlist,
)
from app.integrations.exercism.client import ExerciseSummary
from app.schemas.common import XpAward, XpBalance
from app.schemas.library import ExerciseRunResult
from app.services import challenges as challenges_module
from app.services.challenges import ChallengeService

NOW = datetime(2026, 10, 20, 9, 30, tzinfo=UTC)  # a Tuesday


# --- Rotation rules -------------------------------------------------------------------------------


def test_daily_and_speed_rotate_at_midnight_utc_and_the_boss_weekly():
    assert period_of("daily", NOW) == "2026-10-20"
    assert period_of("boss", NOW) == "2026-W43"
    assert period_bounds("daily", "2026-10-20") == (
        datetime(2026, 10, 20, tzinfo=UTC),
        datetime(2026, 10, 21, tzinfo=UTC),
    )
    starts, ends = period_bounds("boss", "2026-W43")
    assert starts == datetime(2026, 10, 19, tzinfo=UTC)  # Monday
    assert ends - starts == timedelta(days=7)


@pytest.mark.parametrize(
    ("kind", "period"), [("daily", "2026-10-20"), ("speed", "2026-10-20"), ("boss", "2026-W43")]
)
def test_challenge_ids_round_trip(kind, period):
    assert parse_id(challenge_id(kind, period)) == (kind, period)
    # Ids from when each language had its own challenge still open the same one.
    assert parse_id(f"{challenge_id(kind, period)}-python") == (kind, period)


@pytest.mark.parametrize(
    "bad", ["", "daily-2026-13-40-python", "boss-2026-10-20-python", "zone-x", "daily-2026-10-20-"]
)
def test_malformed_challenge_ids_are_rejected(bad):
    assert parse_id(bad) is None


def test_shortlist_is_deterministic_and_stays_in_the_band():
    pool = [Candidate(f"ex{i}", 1 + i % 10) for i in range(40)]
    first = shortlist(pool, "daily:2026-10-20:python", (3, 5), exclude=set())
    assert first == shortlist(list(reversed(pool)), "daily:2026-10-20:python", (3, 5), exclude=set())
    assert all(3 <= next(c.level for c in pool if c.slug == s) <= 5 for s in first)
    assert first != shortlist(pool, "daily:2026-10-21:python", (3, 5), exclude=set())


def test_shortlist_widens_an_empty_band_and_skips_refactoring_katas():
    pool = [Candidate("easy", 1), Candidate("ledger", 2, ("refactoring",)), Candidate("hard", 9)]
    assert shortlist(pool, "s", (2, 3), exclude=set()) == ["easy"]  # nearest level; the kata is skipped
    assert set(shortlist(pool, "s", (5, 5), exclude=set())) == {"easy", "hard"}
    assert shortlist(pool, "s", (1, 2), exclude={"easy"}) == ["hard"]
    assert shortlist([], "s", (1, 2), exclude=set()) == []


def test_boss_names_are_stable():
    assert pick_boss("boss-2026-W43-python") == pick_boss("boss-2026-W43-python")


# --- Service, with in-memory fakes --------------------------------------------------------------------


class FakeClient:
    def __init__(self, exercises, by_track=None):
        self._exercises = exercises
        self._by_track = by_track or {}

    async def exercises(self, track):
        return self._by_track.get(track, self._exercises)


class FakeCache:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def put(self, key, payload, *, ttl_seconds):
        self.data[key] = payload


class FakeLibrary:
    def __init__(self, broken=()):
        self.broken = set(broken)
        self.checked = []
        self.submitted = []

    def gradable(self, language_id):
        return language_id in {"python", "javascript", "typescript", "sql"}

    async def starter_fails(self, language_id, slug):
        self.checked.append(slug)
        return slug not in self.broken

    async def submit(self, user_id, language_id, slug, files):
        self.submitted.append(slug)
        ok = files.get("solution.py") == "ok"
        return ExerciseRunResult(
            status="passed" if ok else "failed", tests=[], passed_count=int(ok), total=1, awarded_xp=0
        )


class FakeAttempts:
    def __init__(self):
        self.docs = {}

    async def get(self, user_id, cid):
        doc = self.docs.get((user_id, cid))
        return dict(doc, cleared=list(doc["cleared"])) if doc else None

    async def start(self, user_id, cid, now, deadline):
        self.docs.setdefault(
            (user_id, cid),
            {"user_id": user_id, "challenge_id": cid, "started_at": now, "deadline": deadline, "cleared": [],
             "tries": 1, "won_at": None, "seconds": None},
        )  # fmt: skip
        return await self.get(user_id, cid)

    async def restart(self, user_id, cid, now, deadline):
        doc = self.docs[(user_id, cid)]
        doc.update(started_at=now, deadline=deadline, cleared=[], tries=doc["tries"] + 1)
        return await self.get(user_id, cid)

    async def clear_stage(self, user_id, cid, slug, now):
        doc = self.docs[(user_id, cid)]
        if doc["won_at"] is None and doc["deadline"] > now and slug not in doc["cleared"]:
            doc["cleared"].append(slug)
        return await self.get(user_id, cid)

    async def mark_won(self, user_id, cid, now, seconds):
        doc = self.docs[(user_id, cid)]
        if doc["won_at"]:
            return False
        doc.update(won_at=now, seconds=seconds)
        return True

    async def counts(self, cid):
        docs = [d for d in self.docs.values() if d["challenge_id"] == cid]
        return len(docs), sum(1 for d in docs if d["won_at"])

    async def fastest(self, cid, limit):
        return []


class FakeUsers:
    def __init__(self):
        self.stats = {}

    async def get_many(self, ids):
        return []

    async def inc_stats(self, user_id, deltas):
        for k, v in deltas.items():
            self.stats[k] = self.stats.get(k, 0) + v


class FakeWallet:
    def __init__(self):
        self.paid = {}

    async def earn(self, user_id, amount, reason, *, reward_key=None, activity=None, sprite=None):
        awarded = 0 if reward_key in self.paid else amount
        self.paid.setdefault(reward_key, amount)
        return XpAward(awarded=awarded, balance=XpBalance(xp=0, lifetime_xp=0))

    async def balance(self, user_id):
        return XpBalance(xp=0, lifetime_xp=0)


class FakeTracker:
    def __init__(self):
        self.events = []

    async def record(self, user_id, event, count=1):
        self.events.append(event)

    async def refresh_achievements(self, user_id):
        pass


class Clock:
    def __init__(self, now):
        self.now = now

    def __call__(self):
        return self.now


@pytest.fixture
def clock(monkeypatch):
    c = Clock(NOW)
    monkeypatch.setattr(challenges_module, "utcnow", c)
    return c


def _service(*, broken=(), by_track=None):
    exercises = [
        ExerciseSummary(f"ex-{lvl}-{i}", f"Exercise {lvl}.{i}", lvl, []) for lvl in range(1, 11) for i in range(4)
    ]
    library = FakeLibrary(broken)
    service = ChallengeService(
        FakeClient(exercises, by_track), FakeCache(), library, None, FakeAttempts(), FakeUsers(), FakeWallet(), FakeTracker()
    )
    return service, library


OK = {"solution.py": "ok"}


async def test_board_has_daily_speed_and_boss_with_the_right_levels(clock):
    service, _ = _service()
    daily, speed, boss = await service.board("u1", "python")
    assert (daily.kind, speed.kind, boss.kind) == ("daily", "speed", "boss")
    assert daily.id == "daily-2026-10-20" and boss.id == "boss-2026-W43"
    assert 3 <= daily.stages[0].level <= 5
    assert speed.stages[0].level <= 2
    assert [s.level for s in boss.stages] == sorted(s.level for s in boss.stages) and len(boss.stages) == 3
    assert boss.boss_name and daily.me.status == "not_started"
    # Same picks for everyone, and on every request.
    again, _, _ = await service.board("u2", "python")
    assert again.stages[0].slug == daily.stages[0].slug


async def test_exercises_whose_starter_code_doesnt_run_are_skipped(clock):
    service, library = _service()
    first = (await service.board("u1", "python"))[0].stages[0].slug
    service2, _ = _service(broken={first})
    assert (await service2.board("u1", "python"))[0].stages[0].slug != first


async def test_untestable_languages_are_shown_but_not_timed(clock):
    service, library = _service()
    board = await service.board("u1", "java")
    assert not board[0].gradable
    with pytest.raises(Exception, match="can't run on this server"):
        await service.start("u1", board[0].id, "java")


async def test_winning_the_daily_challenge_pays_the_bonus_once(clock):
    service, library = _service()
    daily = (await service.board("u1", "python"))[0]
    with pytest.raises(ConflictError):
        await service.submit("u1", daily.id, daily.stages[0].slug, OK, "python")  # clock not started

    started = await service.start("u1", daily.id, "python")
    assert started.me.status == "in_progress"
    clock.now += timedelta(minutes=4)
    failed = await service.submit("u1", daily.id, daily.stages[0].slug, {"solution.py": "nope"}, "python")
    assert not failed.won and failed.challenge.me.status == "in_progress"

    clock.now += timedelta(minutes=1)
    won = await service.submit("u1", daily.id, daily.stages[0].slug, OK, "python")
    assert won.won and won.bonus_xp == 100
    assert won.challenge.me.status == "won" and won.challenge.me.seconds == 300
    assert won.challenge.players == 1 and won.challenge.winners == 1
    assert service.users.stats == {"challenges_won": 1}

    again = await service.submit("u1", daily.id, daily.stages[0].slug, OK, "python")
    assert not again.won and again.bonus_xp == 0


async def test_the_daily_clock_runs_out_and_cant_be_restarted(clock):
    service, _ = _service()
    daily = (await service.board("u1", "python"))[0]
    await service.start("u1", daily.id, "python")
    clock.now += timedelta(minutes=31)
    late = await service.submit("u1", daily.id, daily.stages[0].slug, OK, "python")
    assert not late.won and late.challenge.me.status == "timed_out"
    with pytest.raises(ConflictError):
        await service.start("u1", daily.id, "python")


async def test_a_fast_speed_round_counts_as_a_speed_record(clock):
    service, _ = _service()
    speed = (await service.board("u1", "python"))[1]
    await service.start("u1", speed.id, "python")
    clock.now += timedelta(seconds=95)
    result = await service.submit("u1", speed.id, speed.stages[0].slug, OK, "python")
    assert result.won and result.bonus_xp == 60
    assert service.users.stats == {"challenges_won": 1, "speed_records": 1}


async def test_the_boss_is_beaten_stage_by_stage_and_heals_when_time_runs_out(clock):
    service, _ = _service()
    boss = (await service.board("u1", "python"))[2]
    first, second, third = (s.slug for s in boss.stages)
    await service.start("u1", boss.id, "python")

    skipped = await service.submit("u1", boss.id, third, OK, "python")  # out of order: no progress
    assert not any(s.cleared for s in skipped.challenge.stages)
    await service.submit("u1", boss.id, first, OK, "python")
    await service.submit("u1", boss.id, second, OK, "python")
    assert service.tracker.events == ["boss_stage_cleared", "boss_stage_cleared"]

    clock.now += timedelta(minutes=61)
    view = await service.get("u1", boss.id, "python")
    assert view.me.status == "timed_out" and not any(s.cleared for s in view.stages)

    restarted = await service.start("u1", boss.id, "python")
    assert restarted.me.status == "in_progress" and restarted.me.tries == 2
    for slug in (first, second):
        await service.submit("u1", boss.id, slug, OK, "python")
    won = await service.submit("u1", boss.id, third, OK, "python")
    assert won.won and won.bonus_xp == 400
    assert service.users.stats == {"challenges_won": 1, "bosses_defeated": 1}


async def test_future_and_unknown_challenges_are_not_found(clock):
    service, _ = _service()
    with pytest.raises(NotFoundError):
        await service.get("u1", "daily-2026-10-21", "python")
    with pytest.raises(NotFoundError):
        await service.get("u1", "daily-2026-10-20", "cobol")
    yesterday = await service.get("u1", "daily-2026-10-19", "python")
    assert yesterday.me.status == "ended"
    with pytest.raises(ConflictError):
        await service.start("u1", yesterday.id, "python")


def test_hello_world_is_never_a_challenge():
    assert shortlist([Candidate("hello-world", 1), Candidate("leap", 1)], "s", (1, 1), exclude=set()) == ["leap"]


# --- One challenge, every language ----------------------------------------------------------------


async def test_the_same_challenge_is_served_in_every_language(clock):
    service, _ = _service()
    python = await service.board("u1", "python")
    javascript = await service.board("u1", "javascript")
    java = await service.board("u1", "java")
    for one, two, three in zip(python, javascript, java, strict=True):
        assert one.id == two.id == three.id
        assert [x.slug for x in one.stages] == [x.slug for x in two.stages] == [x.slug for x in three.stages]
    assert (python[0].language, javascript[0].language, java[0].language) == ("python", "javascript", "java")


async def test_switching_language_keeps_the_clock_and_pays_the_bonus_once(clock):
    service, _ = _service()
    daily = (await service.board("u1", "python"))[0]
    started = await service.start("u1", daily.id, "python")
    clock.now += timedelta(minutes=2)

    in_js = await service.get("u1", daily.id, "javascript")
    assert in_js.me.status == "in_progress" and in_js.me.deadline == started.me.deadline
    won = await service.submit("u1", daily.id, daily.stages[0].slug, OK, "javascript")
    assert won.won and won.bonus_xp == 100

    again = await service.submit("u1", daily.id, daily.stages[0].slug, OK, "python")
    assert not again.won and again.bonus_xp == 0
    assert (await service.get("u1", daily.id, "typescript")).me.status == "won"
    # A second language doesn't give a second run: starting it just shows the win.
    assert (await service.start("u1", daily.id, "typescript")).me.status == "won"


async def test_only_exercises_every_language_has_become_challenges(clock):
    shared = [ExerciseSummary(f"shared-{i}", f"Shared {i}", 1 + i % 10, []) for i in range(16)]
    by_track = {
        lang.exercism_track: shared
        + [ExerciseSummary(f"{lang.id}-only-{i}", f"Only {lang.id} {i}", 1 + i % 10, []) for i in range(30)]
        for lang in challenges_module.SHARED_LANGUAGES
    }
    service, _ = _service(by_track=by_track)
    for challenge in await service.board("u1", "go"):
        assert all(stage.slug.startswith("shared-") for stage in challenge.stages)


async def test_exercises_must_work_in_every_graded_language(clock):
    service, library = _service()
    first = (await service.board("u1", "python"))[0].stages[0].slug
    checked_languages = {key.split(":")[1] for key in service.cache.data if key.startswith("check:")}
    assert {"python", "javascript", "typescript"} <= checked_languages
    service2, _ = _service(broken={first})
    assert (await service2.board("u1", "javascript"))[0].stages[0].slug != first


async def test_sql_has_its_own_practice_and_isnt_a_challenge_language(clock):
    service, _ = _service()
    with pytest.raises(Exception, match="own practice"):
        await service.board("u1", "sql")
