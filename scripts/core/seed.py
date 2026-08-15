from argparse import ArgumentParser

from gymhero.config import get_settings
from gymhero.database.db import get_ctx_db
from gymhero.log import get_logger
from gymhero.models.user import User
from scripts.core.catalog import (
    create_body_parts,
    create_exercise_types,
    create_exercises,
    create_levels,
)
from scripts.core.resources import load_exercises, unique_values
from scripts.core.users import create_first_superuser

log = get_logger(__name__)


def seed_database(env: str, limit: int | None = None) -> None:
    """Seed ``env``'s database with the superuser and the exercise catalog.

    The reference catalog (levels, body parts, exercise types) is derived from
    the full CSV; ``limit`` caps only how many exercises are inserted.
    """
    settings = get_settings(env)
    database_url = settings.database_url
    # Log host/db only — never the full URL, which carries the password.
    log.info("Seeding database %s", database_url.split("@")[-1])

    rows = load_exercises()
    exercise_rows = rows[:limit] if limit else rows

    with get_ctx_db(database_url) as session:
        superuser = create_first_superuser(session, settings)
        level_ids = {
            level.name: level.id
            for level in create_levels(session, unique_values(rows, "Level"))
        }
        body_part_ids = {
            body_part.name: body_part.id
            for body_part in create_body_parts(session, unique_values(rows, "BodyPart"))
        }
        exercise_type_ids = {
            exercise_type.name: exercise_type.id
            for exercise_type in create_exercise_types(
                session, unique_values(rows, "Type")
            )
        }
        create_exercises(
            session,
            exercise_rows,
            body_part_ids,
            level_ids,
            exercise_type_ids,
            superuser.id,
        )
    log.info("Database seeded (%d exercises)", len(exercise_rows))


def seed_superuser(env: str) -> User:
    """Seed only the configured first superuser for ``env``."""
    settings = get_settings(env)
    database_url = settings.database_url
    with get_ctx_db(database_url) as session:
        user = create_first_superuser(session, settings)
    log.info("Superuser seeded")
    return user


def build_argparser() -> ArgumentParser:
    parser = ArgumentParser(description="Seed the GymHero database.")
    parser.add_argument(
        "--env",
        default="dev",
        choices=["dev", "test"],
        help="Target environment.",
    )
    parser.add_argument(
        "--target",
        default="all",
        choices=["all", "superuser"],
        help="Seed the full catalog ('all') or only the superuser.",
    )
    return parser
