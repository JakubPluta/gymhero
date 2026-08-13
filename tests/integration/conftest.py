import pytest
from fastapi.testclient import TestClient

from gymhero.log import get_logger
from gymhero.main import app
from gymhero.models import Base
from gymhero.security import create_access_token
from scripts.core.catalog import (
    create_body_parts,
    create_exercise_types,
    create_levels,
)
from scripts.core.resources import load_exercises, unique_values
from scripts.core.seed import seed_database
from scripts.core.users import get_or_create_user

log = get_logger("conftest")


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown(sync_engine):
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    yield
    Base.metadata.drop_all(bind=sync_engine)


@pytest.fixture
def get_test_db(_sync_session_factory):
    db = _sync_session_factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_client():
    # TestClient drives the async app synchronously (via its portal), so route
    # tests stay plain sync functions.
    return TestClient(app)


@pytest.fixture
def seed_test_database():
    seed_database("test", limit=10)


@pytest.fixture
def exercise_rows():
    return load_exercises()


@pytest.fixture
def initial_levels(exercise_rows):
    return unique_values(exercise_rows, "Level")


@pytest.fixture
def seed_levels(get_test_db, initial_levels):
    create_levels(get_test_db, initial_levels)


@pytest.fixture
def initial_body_parts(exercise_rows):
    return unique_values(exercise_rows, "BodyPart")


@pytest.fixture
def seed_body_parts(get_test_db, initial_body_parts):
    create_body_parts(get_test_db, initial_body_parts)


@pytest.fixture
def initial_exercise_types(exercise_rows):
    return unique_values(exercise_rows, "Type")


@pytest.fixture
def seed_exercise_types(get_test_db, initial_exercise_types):
    create_exercise_types(get_test_db, initial_exercise_types)


@pytest.fixture
def valid_jwt_token():
    return f"Bearer {create_access_token('1')}"


@pytest.fixture
def invalid_jwt_token():
    return f"Bearer23 {create_access_token('1')}"


@pytest.fixture
def first_active_superuser(get_test_db):
    return get_or_create_user(
        get_test_db, "admin@admin.com", "admin", "Admin", True, True
    )


@pytest.fixture
def first_inactive_user(get_test_db):
    return get_or_create_user(
        get_test_db, "admin@admin.com", "admin", "Admin", False, False
    )
