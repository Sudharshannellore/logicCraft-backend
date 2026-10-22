import pytest

from app.core.errors import ServiceUnavailableError
from app.services.store import StoreService


def make_store(**kwargs) -> StoreService:
    # The checkout guard runs before any repository is touched, so none are needed here.
    return StoreService(None, None, None, None, None, **kwargs)  # type: ignore[arg-type]


async def test_buying_a_pack_is_refused_without_demo_checkout():
    with pytest.raises(ServiceUnavailableError) as exc:
        await make_store().buy_pack("user-1", "pack-small")
    assert exc.value.code == "payments_unavailable"


async def test_subscribing_is_refused_without_demo_checkout():
    with pytest.raises(ServiceUnavailableError):
        await make_store().subscribe("user-1", "pro", "monthly")
