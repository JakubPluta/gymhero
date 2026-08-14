from types import SimpleNamespace

import pytest

from gymhero.api.authorization import authorize_owner_or_superuser
from gymhero.exceptions import PermissionDeniedError


def _actor(user_id: int, *, is_superuser: bool = False) -> SimpleNamespace:
    return SimpleNamespace(id=user_id, is_superuser=is_superuser)


def _resource(owner_id: int) -> SimpleNamespace:
    return SimpleNamespace(owner_id=owner_id)


@pytest.mark.parametrize(
    "actor, owner_id, allowed",
    [
        (_actor(1), 1, True),  # owner, not superuser
        (_actor(2), 1, False),  # neither owner nor superuser
        (_actor(2, is_superuser=True), 1, True),  # superuser, not owner
        (_actor(1, is_superuser=True), 1, True),  # superuser and owner
    ],
)
def test_authorize_owner_or_superuser(actor, owner_id, allowed) -> None:
    resource = _resource(owner_id)
    if allowed:
        assert authorize_owner_or_superuser(resource, actor) is None
    else:
        with pytest.raises(PermissionDeniedError):
            authorize_owner_or_superuser(resource, actor)


def test_authorize_surfaces_custom_message() -> None:
    with pytest.raises(PermissionDeniedError, match="custom message"):
        authorize_owner_or_superuser(
            _resource(1), _actor(2), message="custom message"
        )
