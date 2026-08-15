from gymhero.log import get_logger
from scripts.core.seed import build_argparser, seed_database, seed_superuser

log = get_logger(__name__)

if __name__ == "__main__":
    args = build_argparser().parse_args()
    log.info("Seeding target=%s env=%s", args.target, args.env)
    if args.target == "superuser":
        seed_superuser(args.env)
    else:
        seed_database(args.env)
