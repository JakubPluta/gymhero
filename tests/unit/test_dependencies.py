from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

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


@pytest.fixture
def default_pagination_params():
    return (0, 10)


@pytest.fixture
def custom_pagination_params():
    return (5, 20)


def test_default_values(default_pagination_params):
    # Testing the default values of skip and limit
    skip, limit = get_pagination_params()
    assert (skip.default, limit.default) == default_pagination_params


def test_custom_values(custom_pagination_params):
    # Testing custom values for skip and limit
    skip, limit = get_pagination_params(
        skip=custom_pagination_params[0], limit=custom_pagination_params[1]
    )
    assert skip, limit == custom_pagination_params


def test_negative_skip():
    # Testing a negative value for skip
    skip, limit = get_pagination_params(skip=-5)

    assert skip, limit.default == (-5, 10)


def test_get_token_valid_token():
    # Arrange
    token = "valid_token"
    expected_payload = TokenPayload(sub="1234567890", username="john_doe")

    # Act
    with patch(
        "jose.jwt.decode", return_value={"sub": "1234567890", "username": "john_doe"}
    ):
        result = get_token(token)

    # Assert
    assert result == expected_payload


def test_get_token_invalid_token():
    # Arrange
    token = "invalid_token"

    # Act and Assert
    with pytest.raises(HTTPException):
        get_token(token)


def test_get_current_user_user_exists(mocker):
    # Mock the dependencies
    db_mock = mocker.Mock(spec=Session)
    token_mock = mocker.Mock()
    token_mock.sub = 1

    # Mock the user_crud.get_one function to return a user
    user_mock = mocker.Mock(spec=User)
    user_crud.get_one = mocker.Mock(return_value=user_mock)

    # Call the function being tested
    result = get_current_user(db=db_mock, token=token_mock)

    # Assert that the function returns the user object
    assert result == user_mock


def test_get_current_user_user_not_found(mocker):
    # Mock the dependencies
    db_mock = mocker.Mock(spec=Session)
    token_mock = mocker.Mock()
    token_mock.sub = 1

    # Mock the user_crud.get_one function to return None
    user_crud.get_one = mocker.Mock(return_value=None)

    # Call the function being tested and assert that it raises an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=db_mock, token=token_mock)

    # Assert that the raised exception has the correct status code and details
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


class MockUser:
    def __init__(self, is_active):
        self.is_active = is_active


def test_get_current_active_user_active_user():
    user = MockUser(is_active=True)
    result = get_current_active_user(current_user=user)
    assert result == user


def test_get_current_active_user_inactive_user():
    user = MockUser(is_active=False)
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(current_user=user)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Inactive user"


def test_get_current_superuser():
    # Test case: current user is a super user
    current_user = User(is_superuser=True)
    result = get_current_superuser(current_user)
    assert result == current_user

    # Test case: current user is not a super user
    current_user = User(is_superuser=False)
    with pytest.raises(HTTPException):
        get_current_superuser(current_user)
