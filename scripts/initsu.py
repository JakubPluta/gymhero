"""Create first user"""

from gymhero.database.db import get_ctx_db
from gymhero.database.session import build_sqlalchemy_database_url_from_settings
from gymhero.log import get_logger
from gymhero.config import get_settings
from scripts.utils import create_first_superuser, get_argparser


log = get_logger(__name__, level="DEBUG")


def seed_superuser(env: str) -> None:
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
        create_first_superuser(database)
    log.info("Database seeded")


if __name__ == "__main__":
    parser = get_argparser()
    args = parser.parse_args()
    env_value = args.env
    log.info("Current ENV value %s", env_value)
    seed_superuser(env_value)
    log.info("Database seeded")
