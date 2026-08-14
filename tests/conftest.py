import asyncio
from collections.abc import Generator
from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from gymhero.config import Settings, get_settings
from gymhero.models import Base

# One async engine (asyncpg) on a Postgres testcontainer drives every DB test.


@pytest.fixture(scope="session")
def _postgres_container() -> Generator[PostgresContainer]:
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def _async_url(_postgres_container: PostgresContainer) -> str:
    host = _postgres_container.get_container_host_ip()
    port = _postgres_container.get_exposed_port(5432)
    return (
        f"postgresql+asyncpg://{_postgres_container.username}:"
        f"{_postgres_container.password}@{host}:{port}/{_postgres_container.dbname}"
    )


async def _create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def engine(_async_url: str) -> AsyncEngine:
    # NullPool: connections open per-operation, so a session-scoped engine is
    # safe to reuse across the per-test event loops.
    async_engine = create_async_engine(_async_url, poolclass=NullPool)
    asyncio.run(_create_schema(async_engine))
    return async_engine


@pytest.fixture
def test_settings() -> Settings:
    return get_settings("test")


@pytest.fixture
def subject() -> str:
    return "user123"


@pytest.fixture
def expires_delta() -> timedelta:
    return timedelta(minutes=30)
