from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from gymhero.database import get_db
from gymhero.main import app
from gymhero.models import Base
from gymhero.models.body_part import BodyPart
from gymhero.models.exercise import ExerciseType
from gymhero.models.level import Level
from gymhero.models.user import User
from tests.helpers import (
    auth_headers,
    create_body_part,
    create_exercise_type,
    create_level,
    create_user,
)

# Fixed reference-catalog names so tests can assert on them without caring about
# insertion order.
LEVEL_NAMES = ("Beginner", "Intermediate", "Advanced")
BODY_PART_NAMES = ("Chest", "Back", "Legs")
EXERCISE_TYPE_NAMES = ("Strength", "Cardio", "Mobility")


@pytest.fixture(autouse=True)
async def _truncate(engine: AsyncEngine) -> AsyncGenerator[None]:
    yield
    tables = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def db(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.fixture
async def client(engine: AsyncEngine) -> AsyncGenerator[AsyncClient]:
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _override_get_db() -> AsyncGenerator[AsyncSession]:
        async with factory() as session:
            yield session

    # Standard FastAPI test wiring: point the app's get_db at the testcontainer.
    app.dependency_overrides[get_db] = _override_get_db
    # raise_app_exceptions=False: behave like a real HTTP client — an unhandled
    # server error comes back as a 500 response, not a re-raised Python exception.
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=True
    ) as http_client:
        yield http_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def superuser(db: AsyncSession) -> User:
    return await create_user(db, is_superuser=True)


@pytest.fixture
async def regular_user(db: AsyncSession) -> User:
    return await create_user(db)


@pytest.fixture
async def other_user(db: AsyncSession) -> User:
    return await create_user(db)


@pytest.fixture
async def inactive_user(db: AsyncSession) -> User:
    return await create_user(db, is_active=False)


@pytest.fixture
async def superuser_headers(superuser: User) -> dict[str, str]:
    return auth_headers(superuser)


@pytest.fixture
async def user_headers(regular_user: User) -> dict[str, str]:
    return auth_headers(regular_user)


@pytest.fixture
async def other_user_headers(other_user: User) -> dict[str, str]:
    return auth_headers(other_user)


@pytest.fixture
async def seeded_levels(db: AsyncSession) -> list[Level]:
    return [await create_level(db, name=name) for name in LEVEL_NAMES]


@pytest.fixture
async def seeded_body_parts(db: AsyncSession) -> list[BodyPart]:
    return [await create_body_part(db, name=name) for name in BODY_PART_NAMES]


@pytest.fixture
async def seeded_exercise_types(db: AsyncSession) -> list[ExerciseType]:
    return [await create_exercise_type(db, name=name) for name in EXERCISE_TYPE_NAMES]
