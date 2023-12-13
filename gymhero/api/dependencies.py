from typing import Tuple

from fastapi import Depends, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from gymhero.config import settings
from gymhero.crud import user_crud
from gymhero.database import get_db
from gymhero.exceptions import _get_credential_exception
from gymhero.models import User
from gymhero.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_pagination_params(
    skip: int = Query(0, ge=0), limit: int = Query(10, gt=0)
) -> Tuple[int, int]:
    """
    Get the pagination parameters.

    Parameters:
        skip (int): The number of items to skip. Defaults to 0.
        limit (int): The maximum number of items to return. Defaults to 10.

    Returns:
        Tuple[int, int]: A tuple containing the skip and limit values.
    """
    return skip, limit


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
    except (jwt.JWTError, ValidationError) as e:
        raise _get_credential_exception(status_code=status.HTTP_403_FORBIDDEN) from e
    return token_data


def get_current_user(
    db: Session = Depends(get_db), token: TokenPayload = Depends(get_token)
) -> User:
    """
    Retrieves the current user based on the provided database session and authentication token.

    Parameters:
        db (Session): The database session to use for querying the user information.
        token (TokenPayload): The authentication token containing the user's identification.

    Returns:
        User: The user object representing the current authenticated user.

    Raises:
        HTTPException: If the user is not found in the database.
    """
    user = user_crud.get_one(db, User.id == token.sub)
    if user is None:
        raise _get_credential_exception(
            status_code=status.HTTP_404_NOT_FOUND, details="User not found"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Returns the current active user.

    Parameters:
        current_user (User, optional): The current user.

    Returns:
        User: The current active user.

    Raises:
        HTTPException: If the user is not active

    """
    if not user_crud.is_active_user(current_user):
        raise _get_credential_exception(
            status_code=status.HTTP_400_BAD_REQUEST,
            details="Inactive user",
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Returns the current superuser.

    Parameters:
        current_user (User, optional): The current user.

    Returns:
        User: The current superuser.

    Raises:
        HTTPException: If the current user is not a super user.

    """
    if not user_crud.is_super_user(current_user):
        raise _get_credential_exception(
            status_code=status.HTTP_403_FORBIDDEN,
            details="The user does not have enough privileges",
        )
    return current_user
