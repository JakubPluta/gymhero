import inspect

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gymhero.database.db import get_ctx_db, get_db
from gymhero.exceptions import SQLAlchemyException


async def test_get_db_yields_async_session(_database_urls, monkeypatch):
    engine = create_async_engine(_database_urls["async"], poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr("gymhero.database.db.async_session_factory", factory)

    agen = get_db()
    assert inspect.isasyncgen(agen)

    session = await agen.__anext__()
    assert isinstance(session, AsyncSession)

    with pytest.raises(StopAsyncIteration):
        await agen.__anext__()

    await engine.dispose()


def test_get_ctx_db(sync_database_url):
    with get_ctx_db(sync_database_url) as db:
        assert isinstance(db, Session)
        assert db.is_active is True

    with pytest.raises(SQLAlchemyException):
        with get_ctx_db(sync_database_url) as db:
            db.add(1)
