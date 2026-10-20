"""Sign-up, sign-in and sessions.

A session is a pair: a short-lived JWT access token sent as `Authorization: Bearer …`, and a
long-lived refresh token that is swapped for a new pair (rotation — each one works once).
"""

import random
import re
from datetime import timedelta

from pymongo.errors import DuplicateKeyError

from app.core.clock import as_utc, new_id, today, utcnow
from app.core.config import Settings
from app.core.errors import ConflictError, TooManyAttemptsError, UnauthorizedError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    needs_rehash,
    new_refresh_token,
    verify_password,
)
from app.domain.economy import STARTER_XP
from app.repositories.auth import LoginFailureRepository, RefreshTokenRepository
from app.repositories.users import UserRepository
from app.schemas.auth import AuthResponse, RefreshTokenDoc, RegisterRequest, TokenPair
from app.schemas.users import UserDoc, WalletState
from app.services.users import UserService, initials

AVATAR_COLORS = ["#7bf542", "#4da3ff", "#a78bfa", "#f5a623", "#ff5c5c", "#3dd68c"]
INVALID_LOGIN = "Invalid email or password."
# How often a signed-in player's "last seen" time is refreshed (it powers the online dot friends see).
PRESENCE_INTERVAL = timedelta(minutes=1)


def new_player(*, user_id: str, username: str, handle: str, email: str, password_hash: str) -> UserDoc:
    """A brand-new learner: no progress yet, a little starter XP."""
    return UserDoc(
        id=user_id,
        username=username,
        handle=handle,
        email=email.lower(),
        password_hash=password_hash,
        avatar_color=random.choice(AVATAR_COLORS),
        avatar_initials=initials(username),
        joined_at=today().isoformat(),
        wallet=WalletState(xp=STARTER_XP, lifetime_xp=0),
    )


def handle_base(username: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", username.lower()).strip("_")[:20]
    return f"@{slug if len(slug) >= 3 else (slug + '_dev')[:20]}"


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        failures: LoginFailureRepository,
        profiles: UserService,
        settings: Settings,
    ):
        self.users = users
        self.refresh_tokens = refresh_tokens
        self.failures = failures
        self.profiles = profiles
        self.settings = settings

    # --- Sessions ---------------------------------------------------------------------------------

    async def _issue(self, user: UserDoc) -> TokenPair:
        access, access_expires = create_access_token(
            user.id, user.token_version, secret=self.settings.jwt_secret, minutes=self.settings.access_token_minutes
        )
        refresh = new_refresh_token()
        now = utcnow()
        refresh_expires = now + timedelta(days=self.settings.refresh_token_days)
        await self.refresh_tokens.insert(
            RefreshTokenDoc(id=hash_refresh_token(refresh), user_id=user.id, created_at=now, expires_at=refresh_expires)
        )
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            access_token_expires_at=access_expires,
            refresh_token_expires_at=refresh_expires,
        )

    async def _respond(self, user: UserDoc) -> AuthResponse:
        return AuthResponse(tokens=await self._issue(user), user=await self.profiles.profile(user.id))

    async def authenticate(self, access_token: str) -> str:
        """The user id behind a valid access token; UnauthorizedError otherwise."""
        user_id, version = decode_access_token(access_token, secret=self.settings.jwt_secret)
        user = await self.users.get(user_id)
        if not user:
            raise UnauthorizedError("This account no longer exists.")
        if user.token_version != version:
            raise UnauthorizedError("This session was signed out. Sign in again.", code="token_revoked")
        now = utcnow()
        if user.last_seen_at is None or now - as_utc(user.last_seen_at) > PRESENCE_INTERVAL:
            await self.users.set_fields(user_id, {"last_seen_at": now})
        return user_id

    # --- Flows --------------------------------------------------------------------------------------

    async def register(self, body: RegisterRequest) -> AuthResponse:
        email = body.email.lower()
        if await self.users.email_taken(email):
            raise ConflictError("An account with this email already exists.", code="email_taken")
        password_hash = await hash_password(body.password)
        base = handle_base(body.username)
        for attempt in range(20):
            handle = base if attempt == 0 else f"{base[:17]}{random.randint(10, 999)}"
            user = new_player(
                user_id=new_id(), username=body.username, handle=handle, email=email, password_hash=password_hash
            )
            try:
                await self.users.insert(user)
                break
            except DuplicateKeyError as exc:
                if "email" in str(exc):
                    raise ConflictError("An account with this email already exists.", code="email_taken") from exc
                # handle taken — try another suffix
        else:
            raise ConflictError("Couldn't create a unique handle — try a different name.")
        return await self._respond(user)

    async def login(self, email: str, password: str) -> AuthResponse:
        email = email.lower()
        if await self.failures.count(email) >= self.settings.login_max_failures:
            raise TooManyAttemptsError(
                f"Too many failed sign-ins. Try again in {self.settings.login_lockout_minutes} minutes."
            )
        user = await self.users.get_by_email(email)
        if not await verify_password(password, user.password_hash if user else None) or not user:
            await self.failures.record(email, utcnow())
            raise UnauthorizedError(INVALID_LOGIN, code="invalid_credentials")
        await self.failures.clear(email)
        if needs_rehash(user.password_hash):  # hashing parameters were upgraded since this password was set
            await self.users.set_password(user.id, await hash_password(password), revoke_sessions=False)
        return await self._respond(user)

    async def refresh(self, refresh_token: str) -> AuthResponse:
        stored = await self.refresh_tokens.take(hash_refresh_token(refresh_token), utcnow())
        user = await self.users.get(stored.user_id) if stored else None
        if not user:
            raise UnauthorizedError("Your session has expired. Sign in again.", code="refresh_invalid")
        return await self._respond(user)

    async def logout(self, refresh_token: str) -> None:
        await self.refresh_tokens.delete(hash_refresh_token(refresh_token))

    async def logout_everywhere(self, user_id: str) -> None:
        """Ends every session: refresh tokens are deleted and existing access tokens stop verifying."""
        await self.refresh_tokens.delete_for_user(user_id)
        await self.users.inc_field(user_id, "token_version", 1)

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> AuthResponse:
        user = await self.users.get(user_id)
        if not user or not await verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Your current password is incorrect.", code="invalid_credentials")
        if current_password == new_password:
            raise ConflictError("Choose a password you haven't used just now.")
        await self.users.set_password(user_id, await hash_password(new_password), revoke_sessions=True)
        await self.refresh_tokens.delete_for_user(user_id)
        return await self._respond(await self.users.get(user_id))  # a fresh session for this device
