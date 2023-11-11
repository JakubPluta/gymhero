from gymhero.database.session import SessionLocal
from gymhero.log import get_logger
from typing import Generator

logger = get_logger(__name__)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        db.close()