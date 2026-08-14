from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from gymhero.config import settings

# The request path is async (asyncpg); the sync engine helpers exist only for
# the offline tooling — Alembic migrations and the seed scripts. Connection URLs
# come from Settings.database_url / .async_database_url.


def get_engine(database_url: str, echo: bool = False) -> Engine:
    return create_engine(database_url, echo=echo)


def get_local_session(database_url: str, echo: bool = False) -> sessionmaker:
    return sessionmaker(
        autocommit=False, autoflush=False, bind=get_engine(database_url, echo)
    )


def get_async_engine(
    database_url: str,
    echo: bool = False,
    *,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_recycle: int = -1,
) -> AsyncEngine:
    return create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
    )


def get_async_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False: response serialization runs after the service commits.
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async_engine = get_async_engine(
    settings.async_database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
)
async_session_factory = get_async_session_factory(async_engine)
