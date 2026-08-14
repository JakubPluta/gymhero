from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from gymhero.config import settings

# bcrypt-only: verifies the existing bcrypt hashes and keeps producing bcrypt.
password_hash = PasswordHash((BcryptHasher(),))


def _create_token(
    subject: str | int, *, token_type: str, expires_delta: timedelta
) -> str:
    to_encode = {
        "sub": str(subject),
        "type": token_type,
        "exp": datetime.now(UTC) + expires_delta,
    }
    return jwt.encode(
        to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM
    )


def create_access_token(
    subject: str | int, expires_delta: timedelta | None = None
) -> str:
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject, token_type="access", expires_delta=delta)


def create_refresh_token(
    subject: str | int, expires_delta: timedelta | None = None
) -> str:
    delta = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(subject, token_type="refresh", expires_delta=delta)


def decode_token(token: str, *, expected_type: str) -> dict[str, Any]:
    """Decode a JWT and assert its ``type`` claim, else raise ``InvalidTokenError``."""
    payload = jwt.decode(
        token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM]
    )
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"expected a {expected_type} token")
    return payload


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
