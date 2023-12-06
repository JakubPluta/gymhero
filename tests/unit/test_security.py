import pytest
from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from gymhero.security import get_password_hash, verify_password, create_access_token


def test_password_hash():
    password = "password123"
    hashed = get_password_hash(password)
    assert password not in hashed


def test_matching_passwords():
    password = "password123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) == True


def test_non_matching_passwords():
    password = "password123"
    hashed = get_password_hash(password)
    assert verify_password("password321", hashed) == False


@pytest.fixture
def subject():
    return "user123"


@pytest.fixture
def expires_delta():
    return timedelta(minutes=30)


@pytest.mark.parametrize(
    "subject, expires_delta",
    [
        ("user123", timedelta(minutes=30)),
        ("user456", None),
    ],
)
def test_create_access_token(subject, expires_delta, test_settings):
    token = create_access_token(subject, expires_delta)

    # Verify that the token is not empty
    assert token is not None

    # Verify that the token is a string
    assert isinstance(token, str)
    print(token)

    # Verify that the token can be decoded
    decoded_token = jwt.decode(
        token,
        test_settings.SECRET_KEY,
        algorithms=[test_settings.ALGORITHM],
        options={"verify_aud": False},
    )
    print(decoded_token)
    assert decoded_token is not None

    # Verify that the token contains the correct subject
    assert decoded_token["sub"] == subject

    # Verify that the token expires in the future
    assert decoded_token["exp"] > datetime.utcnow().timestamp()
