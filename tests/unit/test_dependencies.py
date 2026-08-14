from unittest.mock import patch

import pytest
from fastapi import HTTPException

from gymhero.api.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_current_user,
    get_pagination_params,
    get_token,
)
from gymhero.crud.user import user_crud
from gymhero.models.user import User
from gymhero.schemas.auth import TokenPayload


def test_get_pagination_params_defaults() -> None:
    # Called without DI, the params carry their Query() defaults.
    skip, limit = get_pagination_params()
    assert (skip.default, limit.default) == (0, 10)


def test_get_pagination_params_returns_passed_values() -> None:
    skip, limit = get_pagination_params(skip=5, limit=20)
    assert (skip, limit) == (5, 20)


def test_get_pagination_params_does_not_enforce_bounds_at_call_level() -> None:
    # The ge=0 bound is enforced by FastAPI at request time, not on a direct call.
    skip, limit = get_pagination_params(skip=-5)
    assert (skip, limit.default) == (-5, 10)


def test_get_token_valid_token_returns_payload() -> None:
    expected = TokenPayload(sub=1234567890, type="access")
    with patch("jwt.decode", return_value={"sub": "1234567890", "type": "access"}):
        assert get_token("valid_token") == expected


def test_get_token_invalid_token_raises() -> None:
    with pytest.raises(HTTPException):
        get_token("invalid_token")


async def test_get_current_user_returns_user_when_found(mocker) -> None:
    db_mock = mocker.AsyncMock()
    token_mock = mocker.Mock()
    token_mock.sub = 1
    user_mock = mocker.Mock(spec=User)
    mocker.patch.object(user_crud, "get_one", mocker.AsyncMock(return_value=user_mock))

    result = await get_current_user(db=db_mock, token=token_mock)

    assert result == user_mock


async def test_get_current_user_raises_404_when_missing(mocker) -> None:
    db_mock = mocker.AsyncMock()
    token_mock = mocker.Mock()
    token_mock.sub = 1
    mocker.patch.object(user_crud, "get_one", mocker.AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db=db_mock, token=token_mock)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


class _MockUser:
    def __init__(self, *, is_active: bool) -> None:
        self.is_active = is_active


def test_get_current_active_user_returns_active_user() -> None:
    user = _MockUser(is_active=True)
    assert get_current_active_user(current_user=user) == user


def test_get_current_active_user_rejects_inactive_user() -> None:
    user = _MockUser(is_active=False)
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(current_user=user)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Inactive user"


def test_get_current_superuser_returns_superuser() -> None:
    current_user = User(is_superuser=True)
    assert get_current_superuser(current_user) == current_user


def test_get_current_superuser_rejects_non_superuser() -> None:
    with pytest.raises(HTTPException):
        get_current_superuser(User(is_superuser=False))
