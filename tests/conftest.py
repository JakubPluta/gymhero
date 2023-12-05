from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from gymhero.database import Base
from gymhero.main import app
from gymhero.database.db import get_db


from gymhero.config import get_settings

test_settings = get_settings("test")


TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{test_settings.POSTGRES_USER}:{test_settings.POSTGRES_PASSWORD}\
    @{test_settings.POSTGRES_HOST}:{test_settings.POSTGRES_PORT}/{test_settings.POSTGRES_DB}"


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    print(" gymhero test started ".center(70, "*"))
    print("engine url: ", TEST_SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    print(" gymhero test ended ".center(70, "*"))


engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)


@pytest.fixture
def _engine():
    return engine


@pytest.fixture
def test_session():
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    try:
        db = test_session()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
