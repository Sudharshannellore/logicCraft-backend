"""Framework practice and challenges: quiz generation from docs, and the quiz service's rules."""

from datetime import timedelta

import pytest

from app.core.clock import today, utcnow
from app.core.errors import ConflictError, NotFoundError, UnprocessableError
from app.domain.framework_quiz import candidates, make_questions, shape
from app.domain.live_courses import RawTopic, assemble_course
from app.schemas.common import XpAward, XpBalance
from app.schemas.framework_quiz import QuizAnswer, QuizSubmission
from app.schemas.learning import Lesson, LessonCompletion
from app.services import framework_quiz as fq
from app.services.framework_quiz import FrameworkQuizService
from app.services.learning import apply_progress, progress_percent

# --- generation ----------------------------------------------------------------------------------------------

NAMES = ["useAlpha", "useBravo", "useCharlie", "useDelta", "useEcho", "useFoxtrot", "useGolf", "useHotel"]


def page(prefix="", count=8):
    sentences = [
        f"Use the `{prefix}{NAMES[i]}` hook when you need to manage widget number {i} inside a component." for i in range(count)
    ]
    return "# Title\n\n" + "\n\n".join(sentences)


def test_a_question_blanks_the_term_and_offers_it_among_four_unique_options():
    questions = make_questions({"fw-react-a": page()}, seed="s", count=3, per_page=3)
    assert len(questions) == 3
    for q in questions:
        assert "_____" in q.prompt and "`" not in q.prompt
        assert len(q.options) == 4 and len(set(q.options)) == 4
        assert q.options[q.answer].startswith("use") and q.options[q.answer] in q.explanation
        assert q.lesson_id == "fw-react-a"


def test_generation_is_deterministic_and_the_seed_changes_the_picks():
    a = make_questions({"fw-react-a": page()}, seed="s", count=3, per_page=3)
    assert a == make_questions({"fw-react-a": page()}, seed="s", count=3, per_page=3)
    other = make_questions({"fw-react-a": page()}, seed="different", count=3, per_page=3)
    assert [q.id for q in a] != [q.id for q in other] or [q.options for q in a] != [q.options for q in other]


def test_questions_spread_across_pages():
    pages = {"fw-react-a": page(), "fw-react-b": page(count=8).replace("widget", "gadget")}
    questions = make_questions(pages, seed="s", count=4, per_page=2)
    assert {q.lesson_id for q in questions} == {"fw-react-a", "fw-react-b"}


def test_sentences_that_depend_on_unseen_text_or_are_labels_are_not_quizzed():
    text = (
        "This will generate the files you need in the `app` directory right now, as shown.\n\n"
        "Then call `useAlpha` to configure the widget before anything renders on screen.\n\n"
        "Call `useBravo` to configure the widget before anything renders on screen today."
    )
    assert [c.term for c in candidates(text, "l")] == ["useBravo"]


def test_a_repeated_term_is_ambiguous_and_skipped_but_a_sentence_with_two_terms_is_not():
    repeated = "The `useCharlie` hook is called `useCharlie` in every component that you write for this."
    assert candidates(repeated, "l") == []
    two = "Both `useAlpha` and `useBravo` configure the widget before anything renders on the screen."
    assert {c.term for c in candidates(two, "l")} == {"useAlpha", "useBravo"}


def test_the_other_terms_in_a_sentence_stay_visible_and_are_never_offered_as_answers():
    pages = {"l": "Both `useAlpha` and `useBravo` configure the widget before anything renders on the screen.\n\n" + page()}
    for q in make_questions(pages, seed="s", count=8, per_page=8):
        if q.explanation.startswith("Both"):
            assert ("useBravo" in q.prompt) != ("useAlpha" in q.prompt)
            visible = "useBravo" if "useBravo" in q.prompt else "useAlpha"
            assert visible not in q.options
    # ...and the same sentence is never asked twice.
    prompts = [q.explanation for q in make_questions(pages, seed="s", count=8, per_page=8)]
    assert len(prompts) == len(set(prompts))


def test_wrong_answers_are_the_same_sort_of_thing_as_the_right_one():
    text = (
        "Run `npm run build` to create the production bundle for your project at once.\n\n"
        "Run `npm run dev` to start the development server for your project right away.\n\n"
        "Run `npm run lint` to check the source of your project for common mistakes now.\n\n"
        "Run `npm run test` to execute the unit tests of your project from the terminal.\n\n"
        "Open `src/index.js` to find the entry file of your project, as the setup says.\n\n"
        "Open `src/App.js` to find the root component of your project, as the setup says."
    )
    questions = make_questions({"l": text}, seed="s", count=6, per_page=6)
    commands = [q for q in questions if q.options[q.answer].startswith("npm")]
    assert commands and all(all(o.startswith("npm") for o in q.options) for q in commands)
    # Two paths aren't enough to make a four-option question, so none was asked.
    assert not [q for q in questions if "/" in q.options[q.answer]]


def test_a_page_with_too_few_look_alike_terms_yields_no_questions():
    assert make_questions({"l": page(count=3)}, seed="s", count=3) == []


def test_shapes_tell_commands_paths_files_calls_and_names_apart():
    assert shape("npm run dev", "code") == "command"
    assert shape("src/App.js", "code") == "path"
    assert shape(".env.example", "code") == "file"
    assert shape("map()", "code") == "call"
    assert shape("wire:click", "code") == "prefixed"
    assert shape("ProductTable", "code") == "Cap" and shape("useState", "code") == "ident"
    assert shape("Encoder-only models", "term") == "Cap-multi"


# --- the service ----------------------------------------------------------------------------------------------


class FakeAttempts:
    def __init__(self):
        self.docs: dict[tuple[str, str], dict] = {}

    async def get(self, user_id, quiz_id):
        doc = self.docs.get((user_id, quiz_id))
        return dict(doc) if doc else None

    async def start(self, user_id, quiz_id, *, course_id, kind, now, deadline):
        doc = self.docs.setdefault((user_id, quiz_id), {"course_id": course_id, "kind": kind, "tries": 0})
        doc.update(started_at=now, deadline=deadline, tries=doc["tries"] + 1)
        doc.pop("finished_at", None)
        return dict(doc)

    async def finish(self, user_id, quiz_id, *, course_id, kind, lesson_id, percent, passed, now, seconds):
        doc = self.docs.setdefault((user_id, quiz_id), {"course_id": course_id, "kind": kind, "tries": 0})
        doc.update(finished_at=now, lesson_id=lesson_id, best_percent=max(percent, doc.get("best_percent", 0)))
        if kind == "practice":
            doc["tries"] += 1
        if passed and "passed_at" not in doc:
            doc["passed_at"] = now
            return True
        return False

    async def mark_timed_out(self, user_id, quiz_id, now):
        self.docs[(user_id, quiz_id)]["finished_at"] = now

    async def practice_for_course(self, user_id, course_id):
        return {
            d["lesson_id"]: d
            for (u, _), d in self.docs.items()
            if u == user_id and d["course_id"] == course_id and d["kind"] == "practice" and d.get("lesson_id")
        }

    async def solved_counts(self, user_id):
        out: dict[str, int] = {}
        for (u, _), d in self.docs.items():
            if u == user_id and d["kind"] == "practice" and d.get("passed_at"):
                out[d["course_id"]] = out.get(d["course_id"], 0) + 1
        return out


class FakeCache:
    def __init__(self):
        self.d = {}

    async def get(self, key):
        return self.d.get(key)

    async def put(self, key, payload, *, ttl_seconds):
        self.d[key] = payload


class FakeWallet:
    def __init__(self):
        self.earned: list[tuple[str, int]] = []

    async def earn(self, user_id, amount, reason, *, reward_key=None, **_):
        if any(key == reward_key for key, _ in self.earned):
            return XpAward(awarded=0, balance=XpBalance(xp=0, lifetime_xp=0))
        self.earned.append((reward_key, amount))
        return XpAward(awarded=amount, balance=XpBalance(xp=amount, lifetime_xp=amount))

    async def balance(self, user_id):
        return XpBalance(xp=sum(a for _, a in self.earned), lifetime_xp=0)


class FakeTracker:
    def __init__(self):
        self.events = []

    async def record(self, user_id, event, count=1):
        self.events.append(event)

    async def refresh_achievements(self, user_id):
        pass


class FakeUsers:
    def __init__(self):
        self.stats = []

    async def inc_stats(self, user_id, deltas):
        self.stats.append(deltas)


LESSONS = [f"fw-react-l{i}" for i in range(8)]


def build_live():
    topics = [RawTopic(slug=f"l{i}", name=f"Lesson {i}", kind="doc", level=1 + i, path=f"l{i}.md") for i in range(8)]
    return assemble_course(
        cid="fw-react", title="X", world="X Realm", description="", language_id="javascript", language_name="JavaScript",
        kind="framework", topics=topics,
    )


class FakeLearning:
    def __init__(self):
        self.live = build_live()
        self.completed: set[str] = set()
        self.defeated: set[str] = set()
        self.beaten: list[str] = []
        # Every lesson page has the same shape of material, with page-specific wording.
        self.pages = {f"fw-react-l{i}": page().replace("widget", f"widget{i}x") for i in range(8)}

    def _zones(self):
        return apply_progress(self.live.path.zones, self.completed, self.defeated)

    async def get_course(self, user_id, course_id):
        if course_id != "fw-react":
            raise NotFoundError("Course not found.")
        return self.live.course.model_copy(update={"progress_percent": progress_percent(self._zones())})

    async def list_courses(self, user_id):
        return [await self.get_course(user_id, "fw-react")]

    async def course_path(self, user_id, course_id):
        if course_id != "fw-react":
            raise NotFoundError("Course not found.")
        return self._zones()

    async def lesson_content(self, lesson_id):
        if lesson_id not in self.pages:
            raise NotFoundError("Lesson not found.")
        return Lesson(id=lesson_id, course_id="fw-react", module_id="m", title="t", concept="c", explanation="e", live_content=self.pages[lesson_id])

    async def defeat_boss(self, user_id, course_id, boss_id, *, award_xp=True):
        self.beaten.append(boss_id)
        self.defeated.add(boss_id)
        return LessonCompletion(lesson_id=boss_id, awarded=400, balance=XpBalance(xp=400, lifetime_xp=400), course_progress_percent=0)


@pytest.fixture
def rig():
    learning = FakeLearning()
    wallet, tracker, users = FakeWallet(), FakeTracker(), FakeUsers()
    service = FrameworkQuizService(learning, FakeAttempts(), FakeCache(), wallet, tracker, users)
    return service, learning, wallet, tracker, users


def answers(quiz, correct_for):
    """Answer by looking up the right option (the test knows the cache holds the answers)."""
    return QuizSubmission(answers=[QuizAnswer(question_id=q.id, option_index=correct_for(q)) for q in quiz.questions])


async def right_answers(service, quiz):
    cached = await service.cache.get(next(k for k in service.cache.d if k.startswith(f"fwq:{quiz.id}")))
    truth = {q["id"]: q["answer"] for q in cached}
    return answers(quiz, lambda q: truth[q.id])


async def test_a_practice_quiz_shows_questions_without_answers_and_pays_once_on_the_first_pass(rig):
    service, _, wallet, tracker, _ = rig
    quiz = await service.get("u", "fwq-practice-fw-react-l0")
    assert quiz.kind == "practice" and quiz.available and quiz.status == "not_started" and quiz.time_limit_minutes is None
    assert len(quiz.questions) == 6 and not hasattr(quiz.questions[0], "answer")

    wrong = await service.submit("u", quiz.id, answers(quiz, lambda q: (len(q.options))))  # an impossible option
    assert not wrong.passed and wrong.awarded_xp == 0 and wallet.earned == []
    assert all(not r.correct and r.chosen == 4 for r in wrong.results)

    result = await service.submit("u", quiz.id, await right_answers(service, quiz))
    assert result.passed and result.percent == 100 and result.awarded_xp == 48 and wallet.earned == [("fwquiz:fw-react-l0", 48)]
    assert tracker.events == ["problem_solved"]
    assert all(r.correct and r.explanation for r in result.results)

    again = await service.submit("u", quiz.id, await right_answers(service, quiz))
    assert again.passed and again.awarded_xp == 0
    assert (await service.get("u", quiz.id)).status == "passed"
    assert (await service.get("u", quiz.id)).questions  # a passed practice quiz can be taken again


async def test_practice_topics_list_what_is_solved_and_frameworks_count_it(rig):
    service, *_ = rig
    quiz = await service.get("u", "fwq-practice-fw-react-l1")
    await service.submit("u", quiz.id, await right_answers(service, quiz))
    topics = await service.practice_topics("u", "fw-react")
    assert len(topics) == 8 and [t.lesson_id for t in topics if t.solved] == ["fw-react-l1"]
    assert topics[1].best_percent == 100
    summary = (await service.frameworks("u"))[0]
    assert (summary.course_id, summary.topics, summary.solved) == ("fw-react", 8, 1)


async def test_a_lesson_with_too_little_to_quiz_on_is_marked_unavailable(rig):
    service, learning, *_ = rig
    learning.pages["fw-react-l2"] = "Nothing to quiz on here."
    learning.pages = {**learning.pages}
    for k in list(learning.pages):
        if k != "fw-react-l2":
            learning.pages[k] = "Also nothing."
    quiz = await service.get("u", "fwq-practice-fw-react-l2")
    assert not quiz.available and quiz.questions is None


async def test_unknown_quizzes_are_not_found_and_practice_has_no_clock(rig):
    service, *_ = rig
    for bad in ("nope", "fwq-practice-fw-react-zzz", "fwq-practice-fw-svelte-a", "fwq-zone-fw-react-z9-boss", "fwq-weird-1"):
        with pytest.raises((NotFoundError, ConflictError)):
            await service.get("u", bad)
    with pytest.raises(UnprocessableError):
        await service.start("u", "fwq-practice-fw-react-l0")


async def test_a_zone_boss_is_locked_until_the_zones_topics_are_done(rig):
    service, learning, *_ = rig
    boss = learning.live.path.zones[0].boss.id
    quiz = await service.get("u", f"fwq-zone-{boss}")
    assert quiz.locked and quiz.questions is None and quiz.boss_name
    with pytest.raises(ConflictError):
        await service.start("u", quiz.id)


async def test_beating_a_zone_boss_quiz_defeats_the_boss_and_pays_the_map_reward(rig):
    service, learning, *_ = rig
    zone = learning.live.path.zones[0]
    learning.completed = {n.id for n in zone.nodes}
    quiz_id = f"fwq-zone-{zone.boss.id}"

    with pytest.raises(ConflictError):  # no clock yet
        await service.submit("u", quiz_id, QuizSubmission(answers=[]))
    started = await service.start("u", quiz_id)
    assert started.status == "in_progress" and started.time_limit_minutes == 12 and len(started.questions) >= 3
    assert started.deadline is not None
    assert {q.lesson_id for q in started.questions} <= {n.id for n in zone.nodes}

    result = await service.submit("u", quiz_id, await right_answers(service, started))
    assert result.passed and result.awarded_xp == 400 and learning.beaten == [zone.boss.id]
    assert (await service.get("u", quiz_id)).status == "passed"
    with pytest.raises(ConflictError):  # nothing left to submit
        await service.submit("u", quiz_id, QuizSubmission(answers=[]))


async def test_failing_a_zone_boss_can_be_retried_with_fresh_questions(rig):
    service, learning, *_ = rig
    zone = learning.live.path.zones[0]
    learning.completed = {n.id for n in zone.nodes}
    quiz_id = f"fwq-zone-{zone.boss.id}"
    first = await service.start("u", quiz_id)
    failed = await service.submit("u", quiz_id, QuizSubmission(answers=[]))
    assert not failed.passed and failed.awarded_xp == 0 and learning.beaten == []
    assert (await service.get("u", quiz_id)).status == "failed"
    second = await service.start("u", quiz_id)
    assert second.tries == 2 and second.status == "in_progress"
    assert [q.id for q in first.questions] != [q.id for q in second.questions]


async def test_running_out_of_time_ends_the_run(rig, monkeypatch):
    service, learning, *_ = rig
    zone = learning.live.path.zones[0]
    learning.completed = {n.id for n in zone.nodes}
    quiz_id = f"fwq-zone-{zone.boss.id}"
    await service.start("u", quiz_id)
    later = utcnow() + timedelta(minutes=30)
    monkeypatch.setattr(fq, "utcnow", lambda: later)
    with pytest.raises(ConflictError, match="Time's up"):
        await service.submit("u", quiz_id, QuizSubmission(answers=[]))
    assert (await service.get("u", quiz_id)).status == "failed"


async def test_the_daily_quiz_is_one_run_per_day_with_a_bonus(rig):
    service, _, wallet, _, users = rig
    daily_id = f"fwq-daily-{today().strftime('%Y%m%d')}-fw-react"
    quiz = await service.start("u", daily_id)
    assert quiz.kind == "daily" and quiz.time_limit_minutes == 8 and quiz.xp == 100 and quiz.ends_at
    assert len(quiz.questions) == 5 and len({q.lesson_id for q in quiz.questions}) >= 3
    result = await service.submit("u", daily_id, await right_answers(service, quiz))
    assert result.passed and result.awarded_xp == 100 and users.stats == [{"challenges_won": 1}]
    assert wallet.earned == [(f"fwquiz:{daily_id}", 100)]

    other = await service.start("v", daily_id)
    await service.submit("v", daily_id, QuizSubmission(answers=[]))
    with pytest.raises(ConflictError):  # a failed daily can't be redone
        await service.start("v", daily_id)
    assert [q.id for q in other.questions] == [q.id for q in quiz.questions]  # every player gets the same quiz


async def test_yesterdays_daily_quiz_has_ended(rig):
    service, *_ = rig
    old = (today() - timedelta(days=1)).strftime("%Y%m%d")
    with pytest.raises(ConflictError):
        await service.get("u", f"fwq-daily-{old}-fw-react")


async def test_the_challenge_list_has_the_daily_and_every_zone_boss_without_questions(rig):
    service, learning, *_ = rig
    quizzes = await service.challenges("u", "fw-react")
    zones = learning.live.path.zones
    assert [q.kind for q in quizzes] == ["daily", *["zone"] * len(zones)]
    assert all(q.questions is None for q in quizzes)
    assert quizzes[1].locked and quizzes[1].boss_id == zones[0].boss.id
    with pytest.raises(NotFoundError):
        await service.challenges("u", "fw-nope")


async def test_a_thin_zone_is_filled_out_with_questions_from_the_rest_of_the_framework(rig):
    service, learning, *_ = rig
    zone = learning.live.path.zones[0]
    learning.completed = {n.id for n in zone.nodes}
    for node in zone.nodes:  # the zone's own pages have almost nothing to ask
        learning.pages[node.id] = "Short page."
    started = await service.start("u", f"fwq-zone-{zone.boss.id}")
    assert len(started.questions) >= 3
    assert not {q.lesson_id for q in started.questions} & {n.id for n in zone.nodes}
    assert len({q.id for q in started.questions}) == len(started.questions)


async def test_a_boss_with_nothing_to_quiz_on_can_be_claimed_for_no_xp(rig):
    service, learning, *_ = rig
    zone = learning.live.path.zones[0]
    learning.completed = {n.id for n in zone.nodes}
    quiz_id = f"fwq-zone-{zone.boss.id}"
    with pytest.raises(ConflictError):  # there is a quiz, so fight it
        await service.claim("u", quiz_id)
    learning.pages = {k: "Short page." for k in learning.pages}
    service.cache.d.clear()
    assert not (await service.get("u", quiz_id)).available
    with pytest.raises(UnprocessableError):
        await service.start("u", quiz_id)
    await service.claim("u", quiz_id)
    assert learning.beaten == [zone.boss.id]
    with pytest.raises(UnprocessableError):
        await service.claim("u", "fwq-practice-fw-react-l0")
