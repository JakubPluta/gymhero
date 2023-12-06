from gymhero.log import get_logger
from scripts.core._initdb import seed_database
from scripts.core.utils import get_argparser


log = get_logger(__name__)

if __name__ == "__main__":
    parser = get_argparser()
    args = parser.parse_args()
    env_value = args.env
    log.info("Current ENV value %s", env_value)
    seed_database(env_value)
    log.info("Database seeded")
