import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.common import CamelModel, EpochMs
from app.schemas.users import UserProfile


def check_password_strength(password: str) -> str:
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise ValueError("Use at least one letter and one number.")
    if password.strip() != password:
        raise ValueError("The password can't start or end with a space.")
    return password


class RegisterRequest(CamelModel):
    username: str = Field(min_length=2, max_length=32)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    _strong = field_validator("password")(check_password_strength)

    @field_validator("username")
    @classmethod
    def _clean_username(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise ValueError("Pick a name with at least 2 characters.")
        return value


class LoginRequest(CamelModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(CamelModel):
    refresh_token: str = Field(min_length=20, max_length=200)


class ChangePasswordRequest(CamelModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    _strong = field_validator("new_password")(check_password_strength)


class TokenPair(CamelModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_at: EpochMs
    refresh_token_expires_at: EpochMs


class AuthResponse(CamelModel):
    tokens: TokenPair
    user: UserProfile


class OAuthToken(BaseModel):
    """The OAuth2 password-flow shape (snake_case by spec) — used by the Authorize button in /docs."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in: int


class RefreshTokenDoc(BaseModel):
    id: str  # SHA-256 of the token
    user_id: str
    created_at: datetime
    expires_at: datetime
