"""Domain errors → HTTP responses: the single place status codes are mapped."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from gymhero.exceptions import (
    DomainError,
    EntityConflictError,
    EntityNotFoundError,
    PermissionDeniedError,
)

logger = logging.getLogger(__name__)

# Most-specific first; matched with isinstance.
_STATUS_BY_EXCEPTION: tuple[tuple[type[DomainError], int], ...] = (
    (EntityNotFoundError, status.HTTP_404_NOT_FOUND),
    (EntityConflictError, status.HTTP_409_CONFLICT),
    (PermissionDeniedError, status.HTTP_403_FORBIDDEN),
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        for exc_type, code in _STATUS_BY_EXCEPTION:
            if isinstance(exc, exc_type):
                return JSONResponse(status_code=code, content={"detail": exc.detail})
        logger.error("unmapped domain error: %s", type(exc).__name__, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    @app.exception_handler(SQLAlchemyError)
    async def _handle_database_error(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        # Never leak raw DB/ORM errors to the client.
        logger.error("database error", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected_error(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Catch-all: log the traceback, return a generic 500 (no leak). Runs in the
        # outer ServerErrorMiddleware, so re-attach the request id the middleware set.
        logger.error("unhandled error", exc_info=exc)
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
            headers={"X-Request-ID": request_id} if request_id else None,
        )
