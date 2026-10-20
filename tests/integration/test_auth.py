from tests.integration.conftest import PASSWORD, register

LOGIN = {"email": "sam@example.com", "password": PASSWORD}


async def _sam(http):
    return await register(http, "Sam Park", LOGIN["email"])


async def test_everything_but_the_public_endpoints_needs_a_session(anonymous):
    for path in ("/users/me", "/courses", "/problems", "/tutorials/providers", "/players"):
        response = await anonymous.get(path)
        assert response.status_code == 401, path
        assert response.headers["www-authenticate"] == "Bearer"
    for path in ("/health", "/config/economy", "/activity", "/stats"):
        assert (await anonymous.get(path)).status_code == 200, path
    bad = await anonymous.get("/users/me", headers={"Authorization": "Bearer not-a-token"})
    assert bad.status_code == 401


async def test_register_signs_the_new_player_in(anonymous):
    body = {"username": "Nina Rao", "email": "Nina@Example.com", "password": "learning42"}
    created = await anonymous.post("/auth/register", json=body)
    assert created.status_code == 201
    session = created.json()
    assert session["user"]["email"] == "nina@example.com"
    assert session["user"]["handle"] == "@nina_rao" and session["user"]["xp"] == 0

    me = await anonymous.get("/users/me", headers={"Authorization": f"Bearer {session['tokens']['accessToken']}"})
    assert me.json()["username"] == "Nina Rao"
    wallet = await anonymous.get("/wallet", headers={"Authorization": f"Bearer {session['tokens']['accessToken']}"})
    assert wallet.json()["xp"] == 200  # starter XP

    duplicate = await anonymous.post("/auth/register", json={**body, "email": "nina@example.com"})
    assert duplicate.status_code == 409 and duplicate.json()["error"]["code"] == "email_taken"
    weak = await anonymous.post("/auth/register", json={**body, "email": "x@example.com", "password": "password"})
    assert weak.status_code == 422


async def test_wrong_passwords_are_rejected_then_locked_out(anonymous):
    await _sam(anonymous)
    for _ in range(5):
        wrong = await anonymous.post("/auth/login", json={"email": LOGIN["email"], "password": "nope12345"})
        assert wrong.status_code == 401 and wrong.json()["error"]["message"] == "Invalid email or password."
    locked = await anonymous.post("/auth/login", json=LOGIN)
    assert locked.status_code == 429
    unknown = await anonymous.post("/auth/login", json={"email": "ghost@example.com", "password": "nope12345"})
    assert unknown.status_code == 401 and unknown.json()["error"]["message"] == "Invalid email or password."


async def test_refresh_tokens_rotate_and_logout_ends_the_session(anonymous):
    await _sam(anonymous)
    session = (await anonymous.post("/auth/login", json=LOGIN)).json()
    refresh = session["tokens"]["refreshToken"]

    renewed = await anonymous.post("/auth/refresh", json={"refreshToken": refresh})
    assert renewed.status_code == 200
    assert (await anonymous.post("/auth/refresh", json={"refreshToken": refresh})).status_code == 401  # used once

    new_refresh = renewed.json()["tokens"]["refreshToken"]
    assert (await anonymous.post("/auth/logout", json={"refreshToken": new_refresh})).status_code == 204
    assert (await anonymous.post("/auth/refresh", json={"refreshToken": new_refresh})).status_code == 401


async def test_changing_the_password_signs_out_other_sessions(anonymous):
    old_device = await _sam(anonymous)
    changed = await anonymous.post(
        "/auth/change-password",
        json={"currentPassword": LOGIN["password"], "newPassword": "BrandNew2026"},
        headers=old_device,
    )
    assert changed.status_code == 200
    revoked = await anonymous.get("/users/me", headers=old_device)
    assert revoked.status_code == 401 and revoked.json()["error"]["code"] == "token_revoked"

    new_device = {"Authorization": f"Bearer {changed.json()['tokens']['accessToken']}"}
    assert (await anonymous.get("/users/me", headers=new_device)).status_code == 200
    assert (await anonymous.post("/auth/login", json=LOGIN)).status_code == 401
    relogin = await anonymous.post("/auth/login", json={"email": LOGIN["email"], "password": "BrandNew2026"})
    assert relogin.status_code == 200


async def test_docs_authorize_button_flow(anonymous):
    await _sam(anonymous)
    form = {"username": LOGIN["email"], "password": LOGIN["password"]}
    token = await anonymous.post("/auth/token", data=form)
    assert token.status_code == 200 and token.json()["token_type"] == "bearer"


async def test_two_players_can_befriend_each_other_and_show_as_online(anonymous):
    priya = await register(anonymous, "Priya Sharma", "priya@example.com")
    arjun = await register(anonymous, "Arjun Mehta", "arjun@example.com")
    priya_id = (await anonymous.get("/users/me", headers=priya)).json()["id"]
    sent = await anonymous.post("/social/friend-requests", json={"playerId": priya_id}, headers=arjun)
    assert sent.json()["result"] == "sent"
    social = (await anonymous.get("/social", headers=priya)).json()
    request = next(r for r in social["incomingRequests"] if r["player"]["username"] == "Arjun Mehta")
    await anonymous.post(f"/social/friend-requests/{request['playerId']}/accept", headers=priya)
    arjun_friends = (await anonymous.get("/social", headers=arjun)).json()["friends"]
    assert [(f["username"], f["online"]) for f in arjun_friends] == [("Priya Sharma", True)]
