from collections.abc import AsyncGenerator, Generator
from contextlib import contextmanager

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session

from gymhero.database.session import get_local_session
from gymhero.exceptions import SQLAlchemyException
from gymhero.log import get_logger

log = get_logger(__name__)


async def get_db(request: Request) -> AsyncGenerator[AsyncSession]:
    # The session factory lives on app.state (built in the lifespan handler).
    factory: async_sessionmaker[AsyncSession] = request.app.state.db_session_factory
    async with factory() as db:
        try:
            yield db
        except Exception:
            await db.rollback()  # don't leave a half-applied transaction
            raise


@contextmanager
def get_ctx_db(database_url: str) -> Generator[Session]:
    # Synchronous session for the offline seed scripts.
    db = get_local_session(database_url)()
    try:
        yield db
    except Exception as e:
        log.error("database session error: %s", e)
        raise SQLAlchemyException from e
    finally:
        db.close()
