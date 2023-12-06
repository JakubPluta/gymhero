"""Create first user"""

from argparse import ArgumentParser
import pandas as pd
from sqlalchemy.orm import Session
from gymhero.log import get_logger
from gymhero.models.body_part import BodyPart
from gymhero.models.exercise import Exercise, ExerciseType
from gymhero.models.level import Level
from gymhero.security import get_password_hash
from gymhero.config import settings
from gymhero.crud import user_crud
from gymhero.schemas.user import UserInDB


log = get_logger(__name__, level="DEBUG")


def create_first_superuser(db: Session):
    """Create first superuser"""
    user = user_crud.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)

    if not user:
        user_in = UserInDB(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            full_name=settings.FIRST_SUPERUSER_USERNAME,
        )
        user = user_crud.create(db, obj_create=user_in)
        log.debug("Created first superuser: %s", user)
    else:
        log.debug("First superuser already exists: %s", user)
    return user


def _get_unique_values(dataframe: pd.DataFrame, col: str) -> list:
    """
    Get the unique values from a specific column in a pandas DataFrame.

    Parameters:
        dataframe (pd.DataFrame): The pandas DataFrame from which
        to retrieve the unique values.
        col (str): The name of the column from which to retrieve the unique values.

    Returns:
        list: A list of unique values from the specified column.
    """
    return dataframe[col].unique().tolist()


def create_initial_levels(session: Session, unique_levels: list) -> None:
    """Create initial levels in the database.

    Parameters:
        session (Session): The database session.
        unique_levels (list): A list of unique level names.

    Returns:
        None
    """
    levels = [Level(name=level) for level in unique_levels]
    session.add_all(levels)
    session.commit()
    log.debug("Created %d initial levels", len(levels))
    return levels


def create_initial_body_parts(session: Session, unique_body_parts: list) -> None:
    """
    Create initial body parts in the database.

    Parameters:
        session (Session): The database session object.
        unique_body_parts (list): A list of unique body parts.

    Returns:
        None
    """

    body_parts = [BodyPart(name=body_part) for body_part in unique_body_parts]
    session.add_all(body_parts)
    session.commit()
    log.debug("Created %d initial body parts", len(body_parts))
    return body_parts


def create_initial_exercise_types(
    session: Session, unique_exercise_types: list
) -> None:
    """
    Create initial exercise types in the database.

    Parameters:
        session (Session): The database session object.
        unique_exercise_types (list): A list of unique exercise types.

    Returns:
        None
    """

    exercise_types = [
        ExerciseType(name=exercise_type) for exercise_type in unique_exercise_types
    ]

    session.add_all(exercise_types)
    session.commit()
    log.debug("Created %d initial exercise types", len(exercise_types))
    return exercise_types


def create_initial_exercises(
    session: Session,
    exercises_df: pd.DataFrame,
    bodyparts_dict: dict,
    levels_dict: dict,
    exercise_types_dict: dict,
    owner_id: int,
) -> None:
    """
    Create initial exercises in the database.

    Parameters:
        session (Session): The database session.
        exercises_df (pd.DataFrame): A DataFrame containing exercise data.
        bodyparts_dict (dict): A dictionary mapping body part names to IDs.
        levels_dict (dict): A dictionary mapping exercise levels to IDs.
        exercise_types_dict (dict): A dictionary mapping exercise types to IDs.
        owner_id (int): The ID of the exercise owner.

    Returns:
        None. The function adds exercises to the database and commits the changes.

    """

    exercises = []

    for exercise in exercises_df.itertuples():
        exercise_data = {
            "name": exercise.Title,
            "description": exercise.Desc,
            "target_body_part_id": bodyparts_dict[exercise.BodyPart],
            "exercise_type_id": exercise_types_dict[exercise.Type],
            "level_id": levels_dict[exercise.Level],
            "owner_id": owner_id,
        }
        exercises.append(Exercise(**exercise_data))

    session.add_all(exercises)
    session.commit()


def create_database(session: Session, database: str) -> None:
    """
    Creates a new database if it does not already exist in the PostgreSQL server.

    Parameters:
        session (Session): The active session object used to execute the SQL statement.
        database (str): The name of the database to be created.

    Returns:
        None
    """
    log.debug("Creating database: %s", database)
    record = session.execute(
        f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database}'"
    )
    log.info("Record: %s", record)
    if not record:
        session.execute(f"CREATE DATABASE {database}")
        log.debug("Created database: %s", database)
    else:
        log.debug("Database already exists: %s", database)


def get_argparser() -> ArgumentParser:
    """
    Returns an ArgumentParser object.

    This function creates and configures an ArgumentParser object, which is
    used to parse command line arguments. The function sets up a single
    argument called "--env" that allows the user to specify the environment
    for which to seed the database. The default value for this argument is "dev".
    The argument is stored in the "env" attribute of the parser object.

    Returns:
        ArgumentParser: The configured ArgumentParser object.
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--env",
        default="dev",
        dest="env",
        help="Environment for which to seed the database",
        choices=["dev", "test"],
    )
    return parser
