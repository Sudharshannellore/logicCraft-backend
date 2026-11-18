from typing import Annotated

from fastapi import Depends, Request

from app.api.container import Container
from app.services.demo import DEMO_USER_ID


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

async def get_current_user_id() -> str:
    """The player a request acts as. This is a showcase with no accounts, so it is always the shared demo player."""
    return DEMO_USER_ID


CurrentUser = Annotated[str, Depends(get_current_user_id)]
