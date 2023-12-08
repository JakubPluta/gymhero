from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gymhero.config import get_settings
from gymhero.database import get_db
from gymhero.log import get_logger
from gymhero.main import app
from gymhero.models import Base
from scripts.core._initdb import seed_database
from scripts.core.utils import (
    _get_unique_values,
    create_initial_body_parts,
    create_initial_exercise_types,
    create_initial_levels,
    load_exercise_resource,
)

log = get_logger("conftest")

_test_settings = get_settings("test")


TEST_SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{_test_settings.POSTGRES_USER}:{_test_settings.POSTGRES_PASSWORD}@"
    f"{_test_settings.POSTGRES_HOST}:{_test_settings.POSTGRES_PORT}/{_test_settings.POSTGRES_DB}"
)


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    try:
        Base.metadata.drop_all(bind=engine)
        log.debug("database dropped")
    except Exception:
        pass

    log.debug(" gymhero test started ".center(70, "*"))
    log.debug("engine url: %s", TEST_SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    log.debug(" gymhero test ended ".center(70, "*"))


@pytest.fixture
def _initdb():
    seed_database("test")


@pytest.fixture
def test_settings():
    return get_settings("test")


@pytest.fixture
def subject():
    return "user123"


@pytest.fixture
def expires_delta():
    return timedelta(minutes=30)


engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=False)


TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    try:
        db = TestSession()
        yield db
    finally:
        db.close()


@pytest.fixture
def get_test_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


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
