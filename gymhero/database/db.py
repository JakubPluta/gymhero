from contextlib import contextmanager
from typing import Generator

from gymhero.database.session import SQLALCHEMY_DATABASE_URL, get_local_session
from gymhero.log import get_logger

logger = get_logger(__name__)


def get_db() -> Generator:
    """
    Returns a generator that yields a database session

    Yields:
        Session: A database session object.

    Raises:
        Exception: If an error occurs while getting the database session.
    """

    logger.debug("getting database session")
    db = get_local_session(SQLALCHEMY_DATABASE_URL, False)()
    try:
        yield db
    except Exception as e:
        logger.error(
            "An error occurred while getting the database session. Error: %s", e
        )
        raise e
    finally:
        logger.debug("closing database session")
        db.close()


@contextmanager
def get_ctx_db(database_url: str) -> Generator:
    """
    Context manager that creates a database session and yields
    it for use in a 'with' statement.

    Parameters:
        database_url (str): The URL of the database to connect to.

    Yields:
        Generator: A database session.

    Raises:
        Exception: If an error occurs while getting the database session.

    """
    logger.debug("getting database session")
    db = get_local_session(database_url)()
    try:
        yield db
    except Exception as e:
        logger.error(
            "An error occurred while getting the database session. Error: %s", e
        )
        raise e
    finally:
        logger.debug("closing database session")
        db.close()
