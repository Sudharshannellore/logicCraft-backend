"""Levels and leagues, both derived from lifetime XP (spending XP never costs a level)."""

from math import isqrt

from app.schemas.users import LeagueInfo

LEVEL_XP_UNIT = 25  # reaching level n takes 25·n² lifetime XP


def level_for(lifetime_xp: int) -> int:
    return max(1, isqrt(max(0, lifetime_xp) // LEVEL_XP_UNIT))


def xp_for_level(level: int) -> int:
    return LEVEL_XP_UNIT * level * level


def xp_to_next_level(lifetime_xp: int) -> int:
    """Lifetime XP at which the next level starts (the XP bar's goal)."""
    return xp_for_level(level_for(lifetime_xp) + 1)


# Each league spans [floor, next floor) and splits into divisions III (bottom) → I (top).
LEAGUE_FLOORS: list[tuple[str, int]] = [
    ("bronze", 0),
    ("silver", 1_000),
    ("gold", 2_500),
    ("platinum", 5_000),
    ("diamond", 8_000),
    ("master", 20_000),
]
MASTER_CEILING = 50_000
_ROMAN = {1: "I", 2: "II", 3: "III"}


def league_for(lifetime_xp: int) -> LeagueInfo:
    xp = max(0, lifetime_xp)
    index = max(i for i, (_, floor) in enumerate(LEAGUE_FLOORS) if xp >= floor)
    tier, floor = LEAGUE_FLOORS[index]
    ceiling = LEAGUE_FLOORS[index + 1][1] if index + 1 < len(LEAGUE_FLOORS) else MASTER_CEILING
    third = (ceiling - floor) / 3
    division = 3 - min(2, int((xp - floor) // third)) if xp < ceiling else 1
    return LeagueInfo(tier=tier, division=division, label=f"{tier.capitalize()} {_ROMAN[division]}")
