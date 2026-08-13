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


class DomainError(Exception):
    """Base class for domain / business-rule errors raised by the service layer.

    These exceptions are intentionally transport-agnostic — the service layer
    never imports FastAPI. They are translated into HTTP responses by a single
    handler registered on the app (see ``gymhero.api.error_handlers``), which
    keeps status-code mapping and message redaction in one place instead of
    being copy-pasted into every route.
    """

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class EntityNotFoundError(DomainError):
    """A requested entity does not exist (translated to HTTP 404)."""


class EntityConflictError(DomainError):
    """An entity violates a uniqueness / business constraint (HTTP 409)."""


class PermissionDeniedError(DomainError):
    """The actor is not allowed to perform the action (HTTP 403)."""
