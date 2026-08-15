import jwt
from fastapi import Depends, Query, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero import security
from gymhero.crud import user_crud
from gymhero.database import get_db
from gymhero.exceptions import _get_credential_exception
from gymhero.models import User
from gymhero.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_pagination_params(
    skip: int = Query(0, ge=0), limit: int = Query(10, gt=0, le=100)
) -> tuple[int, int]:
    return skip, limit


def get_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    try:
        payload = security.decode_token(token, expected_type="access")
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError) as e:
        # Authentication failure (missing/invalid/expired token) is 401, not 403.
        raise _get_credential_exception(status_code=status.HTTP_401_UNAUTHORIZED) from e
    return token_data


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: TokenPayload = Depends(get_token)
) -> User:
    user = await user_crud.get_one(db, User.id == token.sub)
    if user is None:
        raise _get_credential_exception(
            status_code=status.HTTP_404_NOT_FOUND, details="User not found"
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not user_crud.is_active_user(current_user):
        raise _get_credential_exception(
            status_code=status.HTTP_400_BAD_REQUEST, details="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not user_crud.is_super_user(current_user):
        raise _get_credential_exception(
            status_code=status.HTTP_403_FORBIDDEN,
            details="The user does not have enough privileges",
        )
    return current_user
