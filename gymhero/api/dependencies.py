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
    return skip, limit


def _get_credential_exception(
    status_code: int = status.HTTP_401_UNAUTHORIZED,
    details: str = "Could not validate credentials",
) -> HTTPException:
    credentials_exception = HTTPException(
        status_code=status_code,
        detail=details,
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise _get_credential_exception()
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise _get_credential_exception()
    user = user_crud.get_one_record(db, User.id == token_data.sub)
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
