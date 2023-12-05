import os
from pathlib import Path
from argparse import ArgumentParser
from functools import partial

import numpy as np
import pandas as pd

from gymhero.config import Settings, get_settings
from gymhero.database.session import build_sqlalchemy_database_url_from_settings
from gymhero.log import get_logger
from gymhero.database.db import get_ctx_db
from scripts.utils import (
    _get_unique_values,
    create_first_superuser,
    create_initial_exercises,
    create_initial_levels,
    create_initial_body_parts,
    create_initial_exercise_types,
)


RESOURCE_DIR_PATH = os.path.join(
    Path(os.path.abspath(__file__)).parent.parent, "resources"
)

log = get_logger(__name__)


def _resolve_settings(env) -> Settings:
    """returns the settings for the specified environment.

    Parameters:
        env (str): The environment for which to
            retrieve the settings.
        Defaults to the value of ENV.

    Returns:
        dict: The settings for the specified environment.
    """
    return get_settings(env)


def seed_database(env):
    """Seeding order:

    1. Levels
    2. BodyParts
    3. ExerciseTypes
    4. Exercises - needs owner (set it to superuser)

    """

    settings = _resolve_settings(env)
    get_db = partial(
        get_ctx_db, database_url=build_sqlalchemy_database_url_from_settings(settings)
    )

    log.info("Seeding database")
    exercise_path = os.path.join(RESOURCE_DIR_PATH, "exercises.csv")
    df = pd.read_csv(exercise_path, header=0, index_col=0)
    df.replace({"": None, "nan": None, "N/A": None, np.nan: None}, inplace=True)
    df.drop_duplicates(subset=["Title"], keep="first", inplace=True)

    exercise_types: list[str] = _get_unique_values(df, "Type")
    body_parts: list[str] = _get_unique_values(df, "BodyPart")
    levels: list[str] = _get_unique_values(df, "Level")

    with get_db() as session:
        superuser = create_first_superuser(session)
        superuser_id = superuser.id

    with get_db() as session:
        levels_dict = {
            level.name: level.id for level in create_initial_levels(session, levels)
        }

    with get_db() as session:
        bodyparts_dict = {
            bodypart.name: bodypart.id
            for bodypart in create_initial_body_parts(session, body_parts)
        }

    with get_db() as session:
        exercise_types_dict = {
            exercise_type.name: exercise_type.id
            for exercise_type in create_initial_exercise_types(session, exercise_types)
        }

    log.debug("Levels: %s", levels_dict)
    log.debug("BodyParts: %s", bodyparts_dict)
    log.debug("ExerciseTypes: %s", exercise_types_dict)

    with get_db() as session:
        create_initial_exercises(
            session, df, bodyparts_dict, levels_dict, exercise_types_dict, superuser_id
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--env",
        default="dev",
        dest="env",
        help="Environment for which to seed the database",
        choices=["dev", "prod"],
    )
    args = parser.parse_args()
    env_value = args.env
    log.info("Current ENV value %s", env_value)
    seed_database(env_value)
    log.info("Database seeded")
