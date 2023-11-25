from typing import Generator

from gymhero.database.session import SessionLocal
from gymhero.log import get_logger

logger = get_logger(__name__)


def get_db() -> Generator:
    """
    Generate the database session.

    This function returns a generator object that provides a database session. The session is created using the `SessionLocal` class.

    Returns:
        Generator: A generator that yields the database session.

    Raises:
        Exception: If an error occurs while creating the session.

    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        db.close()
