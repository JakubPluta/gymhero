"""Create first user"""

from gymhero.database.db import get_ctx_db
from gymhero.database.session import build_sqlalchemy_database_url_from_settings
from gymhero.log import get_logger
from gymhero.config import get_settings
from gymhero.models.user import User
from scripts.core.utils import create_first_superuser


log = get_logger(__name__, level="DEBUG")


def seed_superuser(env: str) -> User:
    """
    Seed the database with a superuser.

    Parameters:
        env (str): The environment to use for seeding the database.

    Returns:
        None: This function does not return anything.
    """

    settings = get_settings(env)
    database_url = build_sqlalchemy_database_url_from_settings(settings)
    with get_ctx_db(database_url) as database:
        usr = create_first_superuser(database)
    log.info("superuser created")
    return usr
