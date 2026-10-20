from tests.integration.conftest import register

TWO_SUM = (
    "def two_sum(nums, target):\n"
    "    seen = {}\n"
    "    for i, n in enumerate(nums):\n"
    "        if target - n in seen:\n"
    "            return [seen[target - n], i]\n"
    "        seen[n] = i\n"
)


async def xp(client, headers=None) -> int:
    return (await client.get("/wallet", headers=headers)).json()["xp"]


async def test_new_profile_matches_the_frontend_contract(client):
    me = (await client.get("/users/me")).json()
    assert {"avatarColor", "xpToNextLevel", "streakDays", "league", "stats", "skills"} <= me.keys()
    assert me["level"] == 1 and me["league"]["label"] == "Bronze III" and me["rank"] == 1
    assert me["email"] == "learner@example.com" and "passwordHash" not in me
    assert me["stats"]["problemsSolved"] == 0


async def test_platform_stats_count_real_players_only(client):
    stats = (await client.get("/stats")).json()
    assert stats == {"learners": 1, "problemsSolved": 0, "bossesDefeated": 0, "languages": 13}
    await client.post("/problems/two-sum/submit", json={"language": "python", "code": TWO_SUM})
    assert (await client.get("/stats")).json()["problemsSolved"] == 1


async def test_solving_a_problem_pays_once_and_hides_hidden_tests(client):
    problem = (await client.get("/problems/two-sum")).json()
    assert all(not t.get("hidden") for t in problem["testCases"])

    before = await xp(client)
    first = (await client.post("/problems/two-sum/submit", json={"language": "python", "code": TWO_SUM})).json()
    assert first["status"] == "passed" and first["awardedXp"] == 100
    assert any(t["input"] == "hidden" for t in first["testResults"])
    again = (await client.post("/problems/two-sum/submit", json={"language": "python", "code": TWO_SUM})).json()
    assert again["awardedXp"] == 0
    assert await xp(client) == before + 100

    wrong = (
        await client.post(
            "/problems/two-sum/run", json={"language": "python", "code": "def two_sum(n, t):\n    return [9]\n"}
        )
    ).json()
    assert wrong["status"] == "failed" and "expected output" in wrong["aiFailureExplanation"]


async def test_sql_submission_is_graded_by_its_result(client):
    good = "SELECT name, salary FROM employees WHERE salary > 80000"
    result = (await client.post("/sql/problems/high-earners/submit", json={"query": good})).json()
    assert result["grade"]["passed"] and result["awardedXp"] == 80
    blocked = (await client.post("/sql/query", json={"query": "DELETE FROM employees"})).json()
    assert blocked["error"] == "Only SELECT queries are allowed in the sandbox."


async def test_lessons_unlock_in_order(client):
    assert (await client.post("/lessons/py3/complete")).status_code == 409
    done = (await client.post("/lessons/py1/complete")).json()
    assert done["awarded"] == 50
    path = (await client.get("/courses/python-mastery/path")).json()
    assert [n["state"] for n in path[0]["nodes"]][:3] == ["completed", "current", "locked"]
    resources = (await client.get("/lessons/py1/resources")).json()
    assert resources["resources"][0]["provider"] == "stub"


async def test_spending_requires_enough_xp(client):
    asks = [
        await client.post(
            "/mentor/ask", json={"context": {"kind": "problem", "problemSlug": "two-sum"}, "question": "hint"}
        )
        for _ in range(25)  # 200 starter XP covers 20 answers
    ]
    refused = [a for a in asks if a.status_code == 402]
    assert len(refused) == 5 and refused[0].json()["error"]["code"] == "insufficient_xp"
    assert await xp(client) == 0


async def test_duel_between_two_players_settles_stakes(anonymous):
    ana = await register(anonymous, "Ana Lee", "ana@example.com")
    ben = await register(anonymous, "Ben Cho", "ben@example.com")
    ben_id = (await anonymous.get("/users/me", headers=ben)).json()["id"]
    ana_id = (await anonymous.get("/users/me", headers=ana)).json()["id"]
    await anonymous.post("/social/friend-requests", json={"playerId": ben_id}, headers=ana)
    await anonymous.post(f"/social/friend-requests/{ana_id}/accept", headers=ben)

    body = {"friendId": ben_id, "problemSlug": "two-sum", "timeLimitMinutes": 10, "stake": 25}
    duel = (await anonymous.post("/duels", json=body, headers=ana)).json()["duel"]
    assert duel["status"] == "pending" and await xp(anonymous, ana) == 175  # stake held
    assert (await anonymous.post(f"/duels/{duel['id']}/accept", headers=ben)).json()["duel"]["status"] == "active"
    await anonymous.post(f"/duels/{duel['id']}/start", headers=ana)
    await anonymous.post(f"/duels/{duel['id']}/start", headers=ben)

    solved = await anonymous.post(
        "/problems/two-sum/submit", json={"language": "python", "code": TWO_SUM, "duelId": duel["id"]}, headers=ana
    )
    assert solved.json()["duel"]["myFinished"]
    final = (await anonymous.post(f"/duels/{duel['id']}/forfeit", headers=ben)).json()
    assert final["status"] == "lost"
    # Ana: 200 − 25 stake + 50 (both stakes) + 40 win bonus + 100 for the problem. Ben: 200 − 25.
    assert await xp(anonymous, ana) == 365 and await xp(anonymous, ben) == 175


async def test_quest_needs_its_tasks_and_advances_with_play(client):
    assert (await client.post("/quests/daily/claim")).status_code == 409
    await client.post("/problems/two-sum/submit", json={"language": "python", "code": TWO_SUM})
    quest = (await client.get("/quests/daily")).json()
    assert any(task["progress"] > 0 for task in quest["tasks"])  # every daily quest has a solve-a-problem task
