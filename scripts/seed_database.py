import contextlib
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gymhero.models import Level, BodyPart
from gymhero.models.exercise import ExerciseType


def prep_session(sqlalchemy_database_url):
    engine = create_engine(sqlalchemy_database_url)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextlib.contextmanager
def get_db(sqlalchemy_database_url):
    session = prep_session(sqlalchemy_database_url)()
    try:
        yield session
    finally:
        session.close()


RESOURCE_DIR_PATH = os.path.join(
    Path(os.path.abspath(__file__)).parent.parent, "resources"
)


def _get_unique_values(dataframe, col):
    return dataframe[col].unique().tolist()


def seed_database(database_url):
    exercise_path = os.path.join(RESOURCE_DIR_PATH, "exercises.csv")
    df = pd.read_csv(exercise_path, header=0, index_col=0)

    exercise_types: list[str] = _get_unique_values(df, "Type")
    body_parts: list[str] = _get_unique_values(df, "BodyPart")
    levels: list[str] = _get_unique_values(df, "Level")

    level_orm_objects = [Level(name=level) for level in levels]
    body_parts_orm_objects = [BodyPart(name=body_part) for body_part in body_parts]
    exercise_types_orm_objects = [
        ExerciseType(name=exercise_type) for exercise_type in exercise_types
    ]

    with get_db(database_url) as session:
        session.add_all(level_orm_objects)
        session.commit()
        session.refresh(level_orm_objects)

    with get_db(database_url) as session:
        session.add_all(body_parts_orm_objects)
        session.commit()
        session.refresh(body_parts_orm_objects)

    with get_db(database_url) as session:
        session.add_all(exercise_types_orm_objects)
        session.commit()
        session.refresh(exercise_types_orm_objects)

    # TODO: add logic for exercises


if __name__ == "__main__":
    database_url = os.environ.get("DATABASE_URL")
    seed_database(database_url)
