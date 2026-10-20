from datetime import UTC, date, datetime, timedelta

import pytest

from app.domain.progression import league_for, level_for, xp_to_next_level
from app.schemas.learning import PathBoss, PathNode, PathZone
from app.schemas.social import DuelDoc, DuelPlayerState
from app.schemas.users import StreakState
from app.services.learning import apply_progress, progress_percent
from app.services.social import decide_winner
from app.services.store import add_months
from app.services.wallet import next_streak


@pytest.mark.parametrize(
    ("xp", "level", "league"),
    [
        (0, 1, "Bronze III"),
        (8420, 18, "Diamond III"),
        (7890, 17, "Platinum I"),
        (25000, 31, "Master III"),
        (42850, 41, "Master I"),
        (99999, 63, "Master I"),
    ],
)
def test_levels_and_leagues_follow_lifetime_xp(xp, level, league):
    assert level_for(xp) == level
    assert league_for(xp).label == league
    assert xp_to_next_level(xp) > xp


def test_streak_extends_on_consecutive_days_and_resets_after_a_gap():
    day = date(2026, 10, 19)
    streak = StreakState(current=12, longest=41, last_active="2026-10-18")
    assert next_streak(streak, day) == StreakState(current=13, longest=41, last_active="2026-10-19")
    assert next_streak(next_streak(streak, day), day).current == 13  # same day: unchanged
    assert next_streak(streak, day + timedelta(days=2)).current == 1
    assert next_streak(StreakState(current=41, longest=41, last_active="2026-10-18"), day).longest == 42


def _zone(zid: str, nodes: list[str]) -> PathZone:
    return PathZone(
        id=zid,
        name=zid,
        tagline="",
        difficulty="easy",
        nodes=[
            PathNode(id=n, title=n, difficulty="easy", xp_reward=10, estimated_minutes=5, lesson_id=n) for n in nodes
        ],
        boss=PathBoss(id=f"{zid}-boss", name="Boss", sprite="slime", challenge="", stages=3, xp_reward=100),
    )


def test_world_map_unlocks_in_order():
    zones = [_zone("z1", ["a", "b"]), _zone("z2", ["c", "d"])]

    fresh = apply_progress(zones, set(), set())
    assert [n.state for n in fresh[0].nodes] == ["current", "locked"]
    assert fresh[0].boss.state == "locked"
    assert all(n.state == "locked" for n in fresh[1].nodes)

    cleared = apply_progress(zones, {"a", "b"}, set())
    assert cleared[0].boss.state == "current"
    assert cleared[1].nodes[0].state == "locked"  # the boss guards the next zone

    beaten = apply_progress(zones, {"a", "b"}, {"z1-boss"})
    assert [n.state for n in beaten[1].nodes] == ["current", "locked"]
    assert progress_percent(beaten) == 50  # 3 of 6 stops


def _duel(a: DuelPlayerState, b: DuelPlayerState) -> DuelDoc:
    now = datetime.now(UTC)
    return DuelDoc(
        id="d",
        challenger_id="a",
        opponent_id="b",
        problem_slug="x",
        time_limit_minutes=10,
        stake=0,
        created_at=now,
        players={"a": a, "b": b},
    )


@pytest.mark.parametrize(
    ("a", "b", "winner"),
    [
        (DuelPlayerState(seconds=100, solved=True), DuelPlayerState(seconds=200, solved=True), "a"),
        (DuelPlayerState(seconds=300, solved=True), DuelPlayerState(seconds=200, solved=True), "b"),
        (DuelPlayerState(seconds=200, solved=True), DuelPlayerState(seconds=200, solved=True), None),
        (DuelPlayerState(solved=False), DuelPlayerState(seconds=500, solved=True), "b"),
        (DuelPlayerState(solved=False), DuelPlayerState(solved=False), None),
    ],
)
def test_duel_winner(a, b, winner):
    assert decide_winner(_duel(a, b)) == winner


def test_add_months_clamps_to_month_end():
    assert add_months(datetime(2026, 1, 31, tzinfo=UTC), 1) == datetime(2026, 2, 28, tzinfo=UTC)
    assert add_months(datetime(2026, 11, 15, tzinfo=UTC), 14) == datetime(2028, 1, 15, tzinfo=UTC)
