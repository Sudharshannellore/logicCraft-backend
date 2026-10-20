import jwt
import pytest
from pydantic import ValidationError

from app.core.errors import UnauthorizedError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    verify_password,
)
from app.schemas.auth import RegisterRequest
from app.services.auth import handle_base

SECRET = "unit-test-secret-" + "x" * 40


async def test_passwords_are_hashed_with_argon2_and_verified():
    hashed = await hash_password("Correct42")
    assert hashed.startswith("$argon2id$") and "Correct42" not in hashed
    assert await verify_password("Correct42", hashed)
    assert not await verify_password("Wrong42", hashed)
    assert not await verify_password("Correct42", None)  # unknown email


def test_access_tokens_round_trip_and_reject_tampering():
    token, _ = create_access_token("user-1", 3, secret=SECRET, minutes=5)
    assert decode_access_token(token, secret=SECRET) == ("user-1", 3)
    with pytest.raises(UnauthorizedError):
        decode_access_token(token, secret="another-secret-" + "y" * 40)
    expired, _ = create_access_token("user-1", 0, secret=SECRET, minutes=-1)
    with pytest.raises(UnauthorizedError) as info:
        decode_access_token(expired, secret=SECRET)
    assert info.value.code == "token_expired"
    refresh_shaped = jwt.encode(
        {"sub": "user-1", "type": "refresh", "iat": 0, "exp": 9999999999}, SECRET, algorithm="HS256"
    )
    with pytest.raises(UnauthorizedError):
        decode_access_token(refresh_shaped, secret=SECRET)


def test_refresh_tokens_are_random_and_stored_hashed():
    a, b = new_refresh_token(), new_refresh_token()
    assert a != b and len(a) > 40
    assert hash_refresh_token(a) != a and len(hash_refresh_token(a)) == 64


@pytest.mark.parametrize("password", ["short1", "onlyletters", "12345678", " spaced123"])
def test_weak_passwords_are_refused(password):
    with pytest.raises(ValidationError):
        RegisterRequest(username="Nina", email="nina@example.com", password=password)


def test_handles_are_derived_from_the_name():
    assert handle_base("Nina Rao") == "@nina_rao"
    assert handle_base("Al") == "@al_dev"
