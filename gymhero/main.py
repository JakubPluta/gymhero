import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import RequestResponseEndpoint
from starlette.middleware.trustedhost import TrustedHostMiddleware

from gymhero.api import (
    auth_router,
    bodypart_router,
    exercise_router,
    exercise_type_router,
    level_router,
    training_plan_router,
    training_unit_router,
    user_router,
)
from gymhero.api.error_handlers import register_exception_handlers
from gymhero.config import settings
from gymhero.database.db import get_db
from gymhero.database.session import async_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await async_engine.dispose()


# Interactive docs + the OpenAPI schema are dev conveniences; hide them in prod
# so the API surface isn't advertised publicly.
_docs_enabled = settings.ENV != "production"
app = FastAPI(
    title="GymHero API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)

register_exception_handlers(app)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def bind_request_id(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    """Bind a per-request id into the log context and echo it back to the client."""
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = request_id
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(exercise_router, prefix="/exercises", tags=["exercise"])
api_v1.include_router(
    exercise_type_router, prefix="/exercise-types", tags=["exercise_types"]
)
api_v1.include_router(user_router, prefix="/users", tags=["users"])
api_v1.include_router(level_router, prefix="/levels", tags=["levels"])
api_v1.include_router(bodypart_router, prefix="/body-parts", tags=["bodyparts"])
api_v1.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1.include_router(
    training_plan_router, prefix="/training-plans", tags=["training_plans"]
)
api_v1.include_router(
    training_unit_router, prefix="/training-units", tags=["training_units"]
)
app.include_router(api_v1)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Liveness probe — process is up."""
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
async def ready(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Readiness probe — database is reachable."""
    await db.execute(text("SELECT 1"))
    return {"status": "ready"}
