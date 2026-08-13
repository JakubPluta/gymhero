from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from gymhero.config import Settings, settings

# The request path is async (asyncpg); the sync URL/engine exist only for the
# offline tooling — Alembic migrations and the seed scripts.


def build_sqlalchemy_database_url_from_settings(_settings: Settings) -> str:
    return (
        f"postgresql://{_settings.POSTGRES_USER}:{_settings.POSTGRES_PASSWORD}"
        f"@{_settings.POSTGRES_HOST}:{_settings.POSTGRES_PORT}/{_settings.POSTGRES_DB}"
    )


def build_async_database_url_from_settings(_settings: Settings) -> str:
    return (
        f"postgresql+asyncpg://{_settings.POSTGRES_USER}:{_settings.POSTGRES_PASSWORD}"
        f"@{_settings.POSTGRES_HOST}:{_settings.POSTGRES_PORT}/{_settings.POSTGRES_DB}"
    )


def get_engine(database_url: str, echo: bool = False) -> Engine:
    return create_engine(database_url, echo=echo)


def get_local_session(database_url: str, echo: bool = False, **kwargs) -> sessionmaker:
    return sessionmaker(
        autocommit=False, autoflush=False, bind=get_engine(database_url, echo)
    )


def get_async_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(database_url, echo=echo, pool_pre_ping=True)


def get_async_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False: response serialization runs after the service commits.
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


SQLALCHEMY_DATABASE_URL = build_sqlalchemy_database_url_from_settings(settings)
ASYNC_SQLALCHEMY_DATABASE_URL = build_async_database_url_from_settings(settings)

async_engine = get_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL)
async_session_factory = get_async_session_factory(async_engine)
