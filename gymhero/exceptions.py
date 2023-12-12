from fastapi import status
from fastapi.exceptions import HTTPException


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


class SQLAlchemyException(Exception):
    pass
