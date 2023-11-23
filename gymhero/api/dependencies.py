from typing import Tuple

from fastapi import Query, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
from jose import jwt
from sqlalchemy.orm import Session
from pydantic import ValidationError

from gymhero.database import get_db
from gymhero.models import User
from gymhero.config import settings
from gymhero.schemas.auth import TokenPayload
from gymhero.crud.user import user_crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")


def get_pagination_params(
    skip: int = Query(0, ge=0), limit: int = Query(10, gt=0)
) -> Tuple[int, int]:
    """
    Get the pagination parameters.

    Args:
        skip (int): The number of items to skip. Defaults to 0.
        limit (int): The maximum number of items to return. Defaults to 10.

    Returns:
        Tuple[int, int]: A tuple containing the skip and limit values.
    """
    return skip, limit


def _get_credential_exception(
    status_code: int = status.HTTP_401_UNAUTHORIZED,
    details: str = "Could not validate credentials",
) -> HTTPException:
    """Create an HTTPException with the given status code and details"""
    credentials_exception = HTTPException(
        status_code=status_code,
        detail=details,
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def get_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """
    Retrieve the token payload from the provided JWT token.

    Parameters:
        token (str, optional): The JWT token. Defaults to the value returned by the `oauth2_scheme` dependency.

    Returns:
        TokenPayload: The decoded token payload.

    Raises:
        HTTPException: If there is an error decoding the token or validating the payload.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise _get_credential_exception(status_code=status.HTTP_403_FORBIDDEN)
    return token_data


def get_current_user(
    db: Session = Depends(get_db), token: TokenPayload = Depends(get_token)
) -> User:
    user = user_crud.get_one(db, User.id == token.sub)
    if user is None:
        raise _get_credential_exception(
            status_code=status.HTTP_404_NOT_FOUND, details="User not found"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not user_crud.is_active_user(current_user):
        raise _get_credential_exception(
            status_code=status.HTTP_400_BAD_REQUEST,
            details="Inactive user",
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not user_crud.is_super_user(current_user):
        raise _get_credential_exception(
            status_code=status.HTTP_400_BAD_REQUEST,
            details="User is not a super user",
        )
    return current_user
