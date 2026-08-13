import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from gymhero.config import get_settings
from gymhero.database import get_db
from gymhero.log import get_logger
from gymhero.main import app
from gymhero.models import Base

# The app runs async (asyncpg); the DB is a testcontainer. Two engines hit the
# same container: async drives the app via the get_db override, sync handles
# schema + seeding (the seed helpers stay synchronous).

log = get_logger("conftest")


@pytest.fixture(scope="session")
def _postgres_container():
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def _database_urls(_postgres_container) -> dict[str, str]:
    host = _postgres_container.get_container_host_ip()
    port = _postgres_container.get_exposed_port(5432)
    user = _postgres_container.username
    password = _postgres_container.password
    dbname = _postgres_container.dbname
    return {
        "sync": f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}",
        "async": f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}",
    }


@pytest.fixture(scope="session", autouse=True)
def _configure_database_env(_postgres_container):
    # Point POSTGRES_* at the container so the seed helpers (which build their
    # connection from get_settings) reach the same DB as the app. Env vars win
    # over the .env.test file.
    overrides = {
        "POSTGRES_HOST": _postgres_container.get_container_host_ip(),
        "POSTGRES_PORT": str(_postgres_container.get_exposed_port(5432)),
        "POSTGRES_USER": _postgres_container.username,
        "POSTGRES_PASSWORD": _postgres_container.password,
        "POSTGRES_DB": _postgres_container.dbname,
    }
    saved = {k: os.environ.get(k) for k in overrides}
    os.environ.update(overrides)
    yield
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture(scope="session")
def sync_engine(_database_urls) -> Engine:
    engine = create_engine(_database_urls["sync"])
    yield engine
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def _wire_app_database(_database_urls):
    # NullPool: each request opens/closes its own asyncpg connection, so there
    # is no pooled connection bound to a stale (per-test) event loop.
    async_engine = create_async_engine(_database_urls["async"], poolclass=NullPool)
    async_session_factory = async_sessionmaker(
        async_engine, expire_on_commit=False, autoflush=False
    )

    async def _override_get_db():
        async with async_session_factory() as db:
            try:
                yield db
            except Exception:
                await db.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def _sync_session_factory(sync_engine) -> sessionmaker:
    return sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)


@pytest.fixture
def sync_database_url(_database_urls) -> str:
    return _database_urls["sync"]


@pytest.fixture
def test_settings():
    return get_settings("test")


@pytest.fixture
def subject():
    return "user123"


@pytest.fixture
def expires_delta():
    from datetime import timedelta

    return timedelta(minutes=30)
