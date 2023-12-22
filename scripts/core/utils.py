"""Create first user"""

from argparse import ArgumentParser
import os
from typing import Optional, Union
from pathlib import Path
import pandas as pd
import numpy as np
from pandas import DataFrame
from sqlalchemy.orm import Session
from gymhero.log import get_logger
from gymhero.models.body_part import BodyPart
from gymhero.models.exercise import Exercise, ExerciseType
from gymhero.models.user import User
from gymhero.models.level import Level
from gymhero.security import get_password_hash
from gymhero.config import settings
from gymhero.crud import user_crud
from gymhero.schemas.user import UserInDB


log = get_logger(__name__)


def _create_first_user(
    db: Session,
    email: str,
    password: str,
    username: Optional[str] = None,
    is_superuser: bool = True,
    is_active: bool = True,
) -> User:
    """Create first user"""
    user = user_crud.get_user_by_email(db, email=email)
    if user:
        log.debug("First user already exists")
        return user

    user_in = UserInDB(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=username,
        is_superuser=is_superuser,
        is_active=is_active,
    )
    user = user_crud.create(db, obj_create=user_in)
    log.debug("Created first user: %s", user)
    return user


def create_first_superuser(db: Session) -> User:
    """Create first superuser"""
    return _create_first_user(
        db,
        email=settings.FIRST_SUPERUSER_EMAIL,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        username=settings.FIRST_SUPERUSER_USERNAME,
        is_superuser=True,
    )


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
        default="local",
        dest="env",
        help="Environment for which to seed the database",
        choices=["dev", "test", "local", "d", "l", "t"],
    )
    return parser


def load_exercise_resource() -> DataFrame:
    """
    Load exercise resource data from the exercises.csv file.

    Returns:
        DataFrame: The loaded exercise resource data.
    """
    resource_dir_path: Union[Path, str] = os.path.join(
        Path(os.path.abspath(__file__)).parent.parent.parent, "resources"
    )
    df: DataFrame = pd.read_csv(
        os.path.join(resource_dir_path, "exercises.csv"),
        header=0,
        index_col=0,
    )
    df.replace(
        {"": None, "nan": None, "N/A": None, np.nan: None},
        inplace=True,
    )
    df.drop_duplicates(subset=["Title"], keep="first", inplace=True)
    return df
