from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from gymhero.models import Base
from gymhero.main import app
from gymhero.database.db import get_db
from gymhero.log import get_logger

from gymhero.config import get_settings
from scripts.core._initdb import seed_database

log = get_logger(__name__)

_test_settings = get_settings("test")


TEST_SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{_test_settings.POSTGRES_USER}:{_test_settings.POSTGRES_PASSWORD}@"
    f"{_test_settings.POSTGRES_HOST}:{_test_settings.POSTGRES_PORT}/{_test_settings.POSTGRES_DB}"
)


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    try:
        Base.metadata.drop_all(bind=engine)
        log.debug("Database dropped")
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
