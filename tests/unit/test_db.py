from typing import Generator
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from gymhero.database.db import get_ctx_db, get_db
from gymhero.exceptions import SQLAlchemyException
from tests.conftest import override_get_db


@patch("gymhero.database.db.get_db", return_value=override_get_db())
def test_get_db(mock_get_db):
    # Test case 1: Check if the function returns a generator
    db = mock_get_db()
    print(db)
    assert isinstance(db, Generator)

    # Test case 2: Check if the generator yields a session object
    session: Session = next(db)
    assert isinstance(session, Session)

    with pytest.raises(StopIteration) as e:
        session = next(db)
    assert e.type == StopIteration


def test_get_ctx_db(test_sqlalchemy_database_url):
    with get_ctx_db(test_sqlalchemy_database_url) as db:
        assert isinstance(db, Session)
        assert db.is_active == True

    with pytest.raises(SQLAlchemyException) as e:
        with get_ctx_db(test_sqlalchemy_database_url) as db:
            db.add(1)
    assert e.type == SQLAlchemyException
