import inspect

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from gymhero.database.db import get_db


async def test_get_db_yields_async_session(
    _async_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = create_async_engine(_async_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr("gymhero.database.db.async_session_factory", factory)

    agen = get_db()
    assert inspect.isasyncgen(agen)

    session = await agen.__anext__()
    assert isinstance(session, AsyncSession)

    with pytest.raises(StopAsyncIteration):
        await agen.__anext__()

    await engine.dispose()
