"""Passwords and tokens.

- Passwords: Argon2id (the OWASP-recommended default), hashed off the event loop.
- Access tokens: short-lived JWTs (HS256). `ver` must match the user's `token_version`, so
  changing the password or signing out everywhere invalidates every token already issued.
- Refresh tokens: random opaque strings. Only their SHA-256 is stored, so a leaked database
  can't be used to sign in.
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.clock import utcnow
from app.core.errors import UnauthorizedError

_hasher = PasswordHasher()
# Verified against when an email isn't registered, so the response time doesn't reveal which emails exist.
_DUMMY_HASH = _hasher.hash("timing-equaliser-not-a-real-password")
ALGORITHM = "HS256"


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(_hasher.hash, password)


async def verify_password(password: str, password_hash: str | None) -> bool:
    def _verify() -> bool:
        try:
            return _hasher.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
        except (VerificationError, InvalidHashError):
            return False

    return await asyncio.to_thread(_verify)


def needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)


def create_access_token(user_id: str, token_version: int, *, secret: str, minutes: int) -> tuple[str, datetime]:
    now = utcnow()
    expires = now + timedelta(minutes=minutes)
    claims = {
        "sub": user_id,
        "ver": token_version,
        "type": "access",
        "iat": now,
        "exp": expires,
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(claims, secret, algorithm=ALGORITHM), expires


def decode_access_token(token: str, *, secret: str) -> tuple[str, int]:
    """(user_id, token_version), or UnauthorizedError for anything invalid or expired."""
    try:
        claims = jwt.decode(token, secret, algorithms=[ALGORITHM], options={"require": ["sub", "exp", "iat"]})
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Your session has expired. Sign in again.", code="token_expired") from exc
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid access token.") from exc
    if claims.get("type") != "access":
        raise UnauthorizedError("Invalid access token.")
    return str(claims["sub"]), int(claims.get("ver", 0))


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
