"""Create first user"""

from gymhero.database.db import get_ctx_db
from gymhero.log import get_logger
from scripts.utils import create_first_superuser


log = get_logger(__name__, level="DEBUG")


if __name__ == "__main__":
    log.info("Creating first superuser")
    with get_ctx_db() as database:
        create_first_superuser(database)
