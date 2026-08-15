from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

# Engine/session factories are built by the caller (the app lifespan for async,
# the offline tooling for sync) — nothing is instantiated at import time. The
# sync helpers exist only for Alembic migrations and the seed scripts.


def get_engine(database_url: str, echo: bool = False) -> Engine:
    return create_engine(database_url, echo=echo)


def get_local_session(database_url: str, echo: bool = False) -> sessionmaker[Session]:
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
