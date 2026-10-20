from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, Services
from app.core.clock import utcnow
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    OAuthToken,
    RefreshRequest,
    RegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, services: Services):
    """Creates an account and signs it in."""
    return await services.auth.register(body)


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, services: Services):
    return await services.auth.login(body.email, body.password)


@router.post(
    "/refresh", response_model=AuthResponse, summary="Swap a refresh token for a new session (each works once)"
)
async def refresh(body: RefreshRequest, services: Services):
    return await services.auth.refresh(body.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="End this session")
async def logout(body: RefreshRequest, services: Services) -> None:
    await services.auth.logout(body.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT, summary="End every session on every device")
async def logout_everywhere(user_id: CurrentUser, services: Services) -> None:
    await services.auth.logout_everywhere(user_id)


@router.post(
    "/change-password", response_model=AuthResponse, summary="Signs out other devices and starts a new session"
)
async def change_password(body: ChangePasswordRequest, user_id: CurrentUser, services: Services):
    return await services.auth.change_password(user_id, body.current_password, body.new_password)


@router.post("/token", response_model=OAuthToken, include_in_schema=False)
async def oauth_token(form: Annotated[OAuth2PasswordRequestForm, Depends()], services: Services):
    """OAuth2 password flow for the Authorize button in /docs: put the email in `username`."""
    session = await services.auth.login(form.username, form.password)
    tokens = session.tokens
    expires_in = int((tokens.access_token_expires_at - utcnow()).total_seconds())
    return OAuthToken(access_token=tokens.access_token, refresh_token=tokens.refresh_token, expires_in=expires_in)
