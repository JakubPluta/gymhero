import os
from pathlib import Path
from functools import partial

import numpy as np
import pandas as pd

from gymhero.config import get_settings
from gymhero.database.session import build_sqlalchemy_database_url_from_settings
from gymhero.log import get_logger
from gymhero.database.db import get_ctx_db
from scripts.core.utils import (
    _get_unique_values,
    create_first_superuser,
    create_initial_exercises,
    create_initial_levels,
    create_initial_body_parts,
    create_initial_exercise_types,
)


RESOURCE_DIR_PATH = os.path.join(
    Path(os.path.abspath(__file__)).parent.parent.parent, "resources"
)

log = get_logger(__name__)


def seed_database(env, limit=None):
    """
    Seed the database with initial data.

    Parameters:
        env (str): The environment in which the database is being seeded.
    """

    settings = get_settings(env)
    database_url = build_sqlalchemy_database_url_from_settings(settings)
    get_db = partial(get_ctx_db, database_url=database_url)
    log.info("Seeding database %s", str(database_url.split("@")[-1]))
    log.info("Seeding database %s", str(database_url))
    exercise_path = os.path.join(RESOURCE_DIR_PATH, "exercises.csv")
    df = pd.read_csv(exercise_path, header=0, index_col=0)
    df.replace({"": None, "nan": None, "N/A": None, np.nan: None}, inplace=True)
    df.drop_duplicates(subset=["Title"], keep="first", inplace=True)

    exercise_types: list[str] = _get_unique_values(df, "Type")
    body_parts: list[str] = _get_unique_values(df, "BodyPart")
    levels: list[str] = _get_unique_values(df, "Level")

    log.debug("Exercise types: %s", exercise_types)
    log.debug("Body parts: %s", body_parts)
    log.debug("Levels: %s", levels)

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

    if limit:
        df = df.head(limit)

    with get_db() as session:
        create_initial_exercises(
            session, df, bodyparts_dict, levels_dict, exercise_types_dict, superuser_id
        )
        log.debug("Exercises seeded")
