from datetime import datetime, timedelta, timezone

import jwt
import pytest

from gymhero.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_does_not_contain_plaintext() -> None:
    password = "password123"
    hashed = get_password_hash(password)
    assert password not in hashed


def test_verify_password_accepts_matching() -> None:
    password = "password123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)


def test_verify_password_rejects_non_matching() -> None:
    hashed = get_password_hash("password123")
    assert not verify_password("password321", hashed)


@pytest.mark.parametrize(
    "subject, expires_delta",
    [
        ("user123", timedelta(minutes=30)),
        ("user456", None),
    ],
)
def test_create_access_token(subject, expires_delta, test_settings) -> None:
    token = create_access_token(subject, expires_delta)

    # Verify that the token is not empty
    assert token is not None

    # Verify that the token is a string
    assert isinstance(token, str)

    # Verify that the token can be decoded
    decoded_token = jwt.decode(
        token,
        test_settings.SECRET_KEY.get_secret_value(),
        algorithms=[test_settings.ALGORITHM],
        options={"verify_aud": False},
    )
    assert decoded_token is not None

    # Verify that the token contains the correct subject and type
    assert decoded_token["sub"] == subject
    assert decoded_token["type"] == "access"

    # Verify that the token expires in the future
    assert decoded_token["exp"] > datetime.now(timezone.utc).timestamp()


def test_create_refresh_token_has_refresh_type(test_settings) -> None:
    token = create_refresh_token("user123")
    decoded = jwt.decode(
        token,
        test_settings.SECRET_KEY.get_secret_value(),
        algorithms=[test_settings.ALGORITHM],
    )
    assert decoded["sub"] == "user123"
    assert decoded["type"] == "refresh"
    assert decoded["exp"] > datetime.now(timezone.utc).timestamp()


def test_decode_token_rejects_wrong_type() -> None:
    access = create_access_token("1")
    # An access token must not pass where a refresh token is expected.
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(access, expected_type="refresh")
    # ...and the happy path returns the payload.
    assert decode_token(access, expected_type="access")["sub"] == "1"
