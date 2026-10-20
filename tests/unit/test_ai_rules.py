from app.domain import mentor, resume_ai
from app.domain.code_review import review
from app.schemas.resumes import ResumeData, ResumeEntry

PROBLEM = mentor.ProblemContext(
    title="Two Sum",
    description="Return the indices of two numbers that add up to target. Exactly one answer exists.",
    tags=["Array", "Hash Table"],
    hints=["Try brute force first.", "A hash map finds complements in O(1)."],
    examples=[{"input": "nums = [2,7], target = 9", "output": "[0,1]"}],
)
FACTS = resume_ai.LearnerFacts(problems_solved=214, accuracy=86, rank=4, league_label="Diamond III", longest_streak=41)


def test_mentor_reveals_the_next_hint_each_turn():
    assert mentor.mentor_reply("hint please", PROBLEM, turn=0) == "Hint: Try brute force first."
    assert mentor.mentor_reply("another hint", PROBLEM, turn=1) == "Hint: A hash map finds complements in O(1)."


def test_mentor_uses_the_first_tag_with_a_known_approach():
    assert "The array approach is better" in mentor.mentor_reply("what's the time complexity?", PROBLEM)


def test_suggestions_forgive_typos_while_typing():
    pool = mentor.suggested_questions(PROBLEM)
    assert mentor.match_suggestions(pool, "complxity")[0] == "What is the time complexity of the best approach?"
    assert mentor.match_suggestions(pool, "") == pool[:4]


def test_improve_bullet_strengthens_the_verb_and_never_invents_numbers():
    assert resume_ai.improve_bullet("worked on the dashboard") == (
        "Built the dashboard, resulting in [measurable impact — e.g. 30% faster load times]."
    )
    assert resume_ai.improve_bullet("fixed 12 bugs.") == "Resolved 12 bugs."


def test_tailoring_reorders_skills_without_adding_any():
    data = ResumeData(
        headline="Developer",
        skills=["Excel", "Python", "Docker"],
        experience=[ResumeEntry(id="e", title="Intern", bullets=["built REST API in Python"])],
    )
    result = resume_ai.tailor_to_job(data, "We use Python, Docker and AWS.", FACTS, ("Backend Dev", "Acme"))
    assert result.matched == ["Python", "Docker"] and result.missing == ["AWS"] and result.score == 67
    tailored = resume_ai.apply_tailoring(data, result)
    assert tailored.skills == ["Python", "Docker", "Excel"]
    assert "Backend Dev role at Acme" in tailored.summary


def test_keyword_matching_respects_word_boundaries():
    data = ResumeData(skills=["Golang"])
    assert resume_ai.match_job(data, "Experience with Go required").matched == []


def test_code_review_spots_nested_loops_and_hash_maps():
    nested = "def f(nums):\n    for i in nums:\n        for j in nums:\n            pass\n"
    linear = "def f(nums):\n    seen = {}\n    for n in nums:\n        seen[n] = 1\n"
    assert review(nested, "python", "f").time_complexity == "O(n²)"
    fast = review(linear, "python", "f")
    assert (fast.time_complexity, fast.space_complexity) == ("O(n)", "O(n)")
    js = "function f(a) {\n  a.forEach((x) => {\n    a.forEach((y) => {})\n  })\n}\n"
    assert review(js, "javascript", "f").time_complexity == "O(n²)"
