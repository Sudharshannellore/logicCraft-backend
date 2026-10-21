"""Turns a live syllabus into a playable course: topics, zones, bosses. No I/O.

Nothing here is written per language or per framework. A course is an ordered list of topics (from an
Exercism track's syllabus, or from a framework's open-source docs); the list is chunked into zones, each
guarded by a boss. Adding a language or a framework never touches this file.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.domain.challenges import BOSS_NAMES, BOSS_SPRITES
from app.domain.languages import LanguageInfo
from app.integrations.exercism.client import Syllabus
from app.schemas.common import Difficulty
from app.schemas.learning import Course, CourseModule, CoursePath, PathBoss, PathNode, PathZone

COURSE_PREFIX = "live-"
TARGET_TOPICS = 32
MAX_CONCEPT_TOPICS = 24
MIN_PRACTICE_TOPICS = 8
MIN_TOPICS = 4
ZONE_SIZE = 4
MAX_ZONE_SIZE = 6  # a documentation section bigger than this is split into several zones

NODE_XP: dict[Difficulty, int] = {"easy": 50, "medium": 100, "hard": 150}
NODE_MINUTES: dict[Difficulty, int] = {"easy": 10, "medium": 18, "hard": 25}
BOSS_STAGES: dict[Difficulty, int] = {"easy": 3, "medium": 4, "hard": 4}
BOSS_XP: dict[Difficulty, int] = {"easy": 250, "medium": 400, "hard": 600}
ZONE_NAMES = (
    "Starter Meadows",
    "Syntax Woods",
    "Logic Hills",
    "Function Falls",
    "Data Canyon",
    "Pattern Peaks",
    "Refactor Ridge",
    "Algorithm Keep",
    "Edge-Case Marsh",
    "Optimizer Summit",
)

TopicKind = Literal["concept", "practice", "doc"]


@dataclass(frozen=True)
class Topic:
    slug: str
    name: str
    kind: TopicKind
    level: int  # 1–10
    concepts: tuple[str, ...]
    module_id: str
    # Documentation topics only: the page's file in its repository, and the section it sits in.
    path: str = ""
    section: str | None = None


@dataclass(frozen=True)
class RawTopic:
    """A topic before it is placed on the map."""

    slug: str
    name: str
    kind: TopicKind
    level: int
    concepts: tuple[str, ...] = ()
    path: str = ""
    section: str | None = None


@dataclass(frozen=True)
class LiveCourse:
    course: Course
    path: CoursePath
    topics: dict[str, Topic]  # by node id


def course_id(language_id: str) -> str:
    return f"{COURSE_PREFIX}{language_id}"


def node_id(language_id: str, slug: str) -> str:
    return f"{COURSE_PREFIX}{language_id}-{slug}"


def parse_id(item_id: str) -> tuple[str, str] | None:
    """`live-python-basics` → ("python", "basics"); `live-python` → ("python", ""). None for any other id."""
    if not item_id.startswith(COURSE_PREFIX):
        return None
    language_id, _, rest = item_id.removeprefix(COURSE_PREFIX).partition("-")
    return (language_id, rest) if language_id else None


def difficulty_for(level: float) -> Difficulty:
    return "easy" if level <= 3 else "medium" if level <= 6 else "hard"


def _in_teaching_order(exercises: Sequence) -> list:
    """Concept exercises sorted so each comes after the ones that teach its prerequisites (config order otherwise)."""
    taught_by_someone = {c for e in exercises for c in e.concepts}
    remaining, known, ordered = list(exercises), set(), []
    while remaining:
        ready = next(
            (e for e in remaining if all(p in known or p not in taught_by_someone for p in e.prerequisites)),
            remaining[0],  # a prerequisite cycle in the upstream data must not hang the course
        )
        remaining.remove(ready)
        known.update(ready.concepts)
        ordered.append(ready)
    return ordered


def _spread[T](items: Sequence[T], count: int) -> list[T]:
    """`count` items spaced evenly across `items`, keeping their order."""
    if count >= len(items):
        return list(items)
    if count <= 0:
        return []
    return [items[(i * len(items)) // count] for i in range(count)]


def select_topics(syllabus: Syllabus) -> list[tuple[str, str, TopicKind, int, tuple[str, ...]]]:
    """[(slug, name, kind, level, concepts)] in learning order."""
    concept_exercises = _in_teaching_order(syllabus.concept_exercises)[:MAX_CONCEPT_TOPICS]
    taken = {e.slug for e in concept_exercises}
    topics: list[tuple[str, str, TopicKind, int, tuple[str, ...]]] = [
        # Concept exercises are introductions: they span levels 1–4 in syllabus order.
        (e.slug, e.name, "concept", 1 + round(3 * i / max(1, len(concept_exercises) - 1)), tuple(e.concepts))
        for i, e in enumerate(concept_exercises)
    ]
    practice = sorted((e for e in syllabus.practice if e.slug not in taken), key=lambda e: (e.difficulty, e.name))
    wanted = max(MIN_PRACTICE_TOPICS, TARGET_TOPICS - len(topics))
    topics += [(e.slug, e.name, "practice", e.difficulty, tuple(e.topics)) for e in _spread(practice, wanted)]
    return topics


def ramp_levels(count: int) -> list[int]:
    """Difficulty 1–10 rising evenly over a course's topics (documentation has no difficulty of its own)."""
    return [1 + round(9 * i / max(1, count - 1)) for i in range(count)]


def _chunks(items: list, size: int) -> list[list]:
    chunks = [items[i : i + size] for i in range(0, len(items), size)]
    if len(chunks) > 1 and len(chunks[-1]) < 2:  # no zone with a single topic
        chunks[-2] += chunks.pop()
    return chunks


def _sectioned_zones(topics: list[RawTopic]) -> list[tuple[str, list[RawTopic]]]:
    """Zones named after the documentation sections they cover; big sections become several zones."""
    groups: list[tuple[str, list[RawTopic]]] = []
    for topic in topics:
        name = topic.section or "More"
        if groups and groups[-1][0] == name:
            groups[-1][1].append(topic)
        else:
            groups.append((name, [topic]))
    zones: list[tuple[str, list[RawTopic]]] = []
    for name, items in groups:
        parts = max(1, -(-len(items) // MAX_ZONE_SIZE))
        size = -(-len(items) // parts)
        for p in range(parts):
            zones.append((name if p == 0 else f"{name} {'I' * (p + 1)}", items[p * size : (p + 1) * size]))
    merged: list[tuple[str, list[RawTopic]]] = []
    for name, items in zones:
        if len(items) < 2 and merged:  # a one-topic zone joins the zone before it
            merged[-1][1].extend(items)
        else:
            merged.append((name, list(items)))
    if len(merged) > 1 and len(merged[0][1]) < 2:  # ...or, at the start, the zone after it
        merged[1][1][:0] = merged.pop(0)[1]
    return merged


def _plain_zones(topics: list[RawTopic]) -> list[tuple[str, list[RawTopic]]]:
    return [
        (ZONE_NAMES[z] if z < len(ZONE_NAMES) else f"Frontier {z + 1}", chunk)
        for z, chunk in enumerate(_chunks(topics, ZONE_SIZE))
    ]


def assemble_course(
    *,
    cid: str,
    title: str,
    world: str,
    description: str,
    language_id: str,
    language_name: str,
    kind: Literal["language", "framework"],
    topics: list[RawTopic],
) -> LiveCourse | None:
    """The course, its map and its topics. Node ids are `<course id>-<topic slug>`."""
    if len(topics) < MIN_TOPICS:
        return None
    sectioned = any(t.section for t in topics)
    plan = _sectioned_zones(topics) if sectioned else _plain_zones(topics)

    zones, modules, placed = [], [], {}
    hardest = 0.0  # zones never get easier as the map goes on, even where practice exercises restart at level 1
    for z, (zone_name, chunk) in enumerate(plan, start=1):
        zone_id, module_id = f"{cid}-z{z}", f"{cid}-m{z}"
        hardest = max(hardest, sum(t.level for t in chunk) / len(chunk))
        difficulty = difficulty_for(hardest)
        nodes = []
        for t in chunk:
            nid, node_difficulty = f"{cid}-{t.slug}", difficulty_for(t.level)
            placed[nid] = Topic(t.slug, t.name, t.kind, t.level, t.concepts, module_id, t.path, t.section)
            nodes.append(
                PathNode(
                    id=nid,
                    title=t.name,
                    difficulty=node_difficulty,
                    xp_reward=NODE_XP[node_difficulty],
                    estimated_minutes=NODE_MINUTES[node_difficulty],
                    lesson_id=nid,
                )
            )
        stages = BOSS_STAGES[difficulty]
        zones.append(
            PathZone(
                id=zone_id,
                name=zone_name,
                tagline="Covers " + ", ".join(t.name for t in chunk[:3]) + ("…" if len(chunk) > 3 else "."),
                difficulty=difficulty,
                nodes=nodes,
                boss=PathBoss(
                    id=f"{zone_id}-boss",
                    name=BOSS_NAMES[(z - 1) % len(BOSS_NAMES)],
                    sprite=BOSS_SPRITES[(z - 1) % len(BOSS_SPRITES)],
                    challenge=f"Beat {stages} {difficulty} {language_name} challenges in a row",
                    stages=stages,
                    xp_reward=BOSS_XP[difficulty],
                ),
            )
        )
        modules.append(CourseModule(id=module_id, title=zone_name, lessons_count=len(nodes), exercises_count=0))

    course = Course(
        id=cid,
        title=title,
        world=world,
        description=description,
        language=language_id,
        total_xp=sum(n.xp_reward for z in zones for n in z.nodes) + sum(z.boss.xp_reward for z in zones),
        modules=modules,
        kind=kind,
    )
    return LiveCourse(course=course, path=CoursePath(course_id=cid, zones=zones), topics=placed)


def build_live_course(info: LanguageInfo, syllabus: Syllabus) -> LiveCourse | None:
    """A language's course from its Exercism syllabus."""
    selected = select_topics(syllabus)
    live = assemble_course(
        cid=course_id(info.id),
        title=f"{info.name} Live Course",
        world=f"{info.name} Frontier",
        description=(
            f"Follow Exercism's open-source {info.name} syllabus: concept lessons and graded exercises, "
            "pulled live so it grows as the track does."
        ),
        language_id=info.id,
        language_name=info.name,
        kind="language",
        topics=[RawTopic(slug, name, kind, level, concepts) for slug, name, kind, level, concepts in selected],
    )
    if live is None:
        return None
    # Every topic of a language course ends with a graded exercise.
    modules = [m.model_copy(update={"exercises_count": m.lessons_count}) for m in live.course.modules]
    return LiveCourse(live.course.model_copy(update={"modules": modules}), live.path, live.topics)
