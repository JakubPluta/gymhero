from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from gymhero.config import get_settings
from gymhero.log import get_logger
from gymhero.main import app
from gymhero.models import Base
from gymhero.security import create_access_token
from scripts.core._initdb import seed_database
from scripts.core.utils import (
    _create_first_user,
    _get_unique_values,
    create_initial_body_parts,
    create_initial_exercise_types,
    create_initial_levels,
    load_exercise_resource,
)
from tests.conftest import engine

log = get_logger("conftest")


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    try:
        Base.metadata.drop_all(bind=engine)
        log.debug("database dropped")
    except Exception:
        pass
    log.debug("engine url %s", str(engine.url))
    log.debug(" gymhero test started ".center(70, "*"))
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    log.debug(" gymhero test ended ".center(70, "*"))


@pytest.fixture
def seed_test_database():
    seed_database("test", limit=10)


@pytest.fixture
def test_settings():
    return get_settings("test")


@pytest.fixture
def subject():
    return "user123"


@pytest.fixture
def expires_delta():
    return timedelta(minutes=30)


@pytest.fixture
def get_test_db(_test_session):
    db = _test_session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def exercises_df():
    return load_exercise_resource()


@pytest.fixture
def initial_levels(exercises_df):
    return _get_unique_values(exercises_df, "Level")


@pytest.fixture
def seed_levels(get_test_db, initial_levels):
    create_initial_levels(get_test_db, initial_levels)


@pytest.fixture
def initial_body_parts(exercises_df):
    return _get_unique_values(exercises_df, "BodyPart")


@pytest.fixture
def seed_body_parts(get_test_db, initial_body_parts):
    create_initial_body_parts(get_test_db, initial_body_parts)


@pytest.fixture
def initial_exercise_types(exercises_df):
    return _get_unique_values(exercises_df, "Type")


@pytest.fixture
def seed_exercise_types(get_test_db, initial_exercise_types):
    create_initial_exercise_types(get_test_db, initial_exercise_types)


@pytest.fixture
def valid_jwt_token():
    token = create_access_token("1")
    return f"Bearer {token}"


@pytest.fixture
def invalid_jwt_token():
    token = create_access_token("1")
    return f"Bearer23 {token}"


@pytest.fixture
def first_active_superuser(get_test_db):
    return _create_first_user(
        get_test_db, "admin@admin.com", "admin", "Admin", True, True
    )


@pytest.fixture
def first_incative_superuser(get_test_db):
    return _create_first_user(
        get_test_db, "admin@admin.com", "admin", "Admin", True, False
    )


@pytest.fixture
def first_incative_user(get_test_db):
    return _create_first_user(
        get_test_db, "admin@admin.com", "admin", "Admin", False, False
    )


@pytest.fixture
def first_incative_superuser(get_test_db):
    return _create_first_user(
        get_test_db, "admin@admin.com", "admin", "Admin", True, False
    )
