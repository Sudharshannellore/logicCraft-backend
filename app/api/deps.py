from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.api.container import Container
from app.core.config import get_settings
from app.core.errors import UnauthorizedError


def get_container(request: Request) -> Container:
    state = request.app.state
    return Container(
        db=state.mongo.db,
        settings=state.settings,
        http=state.http,
        executor=state.executor,
        providers=state.providers,
    )


Services = Annotated[Container, Depends(get_container)]

# Reads `Authorization: Bearer <access token>`. tokenUrl powers the Authorize button in /docs.
bearer = OAuth2PasswordBearer(tokenUrl=f"{get_settings().api_prefix}/auth/token", auto_error=False)


async def get_current_user_id(services: Services, token: Annotated[str | None, Depends(bearer)]) -> str:
    """The signed-in player. Every protected route depends on this (directly or via its router)."""
    if not token:
        raise UnauthorizedError("Sign in to continue.", code="not_authenticated")
    return await services.auth.authenticate(token)


CurrentUser = Annotated[str, Depends(get_current_user_id)]
