from typing import Optional, List

from gymhero.models.exercise import Exercise, ExerciseType
from sqlalchemy.orm import Session
from gymhero.schemas.exercise import (
    ExerciseInDB,
    ExerciseTypeUpdate,
    ExerciseTypeCreate,
    ExerciseTypeBase,
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseTypeInDB,
    ExerciseBase,
)
from logging import getLogger


log = getLogger(__name__)


def create_exercise_type(
    db: Session, exercise_type: ExerciseTypeCreate
) -> ExerciseType:
    log.info("creating exercise type")
    exercise_type_data: dict = exercise_type.model_dump()
    exercise_type_orm: ExerciseType = ExerciseType(**exercise_type_data)
    db.add(exercise_type_orm)
    db.commit()
    db.refresh(exercise_type_orm)
    return exercise_type_orm


def get_all_exercise_types(db: Session) -> List[ExerciseType]:
    return db.query(ExerciseType).all()


def get_exercise_type_by_id(
    db: Session, exercise_type_id: int
) -> Optional[ExerciseType]:
    return db.query(ExerciseType).filter(ExerciseType.id == exercise_type_id).first()


def get_exercise_type_by_name(
    db: Session, exercise_type_name: str
) -> Optional[ExerciseType]:
    return (
        db.query(ExerciseType).filter(ExerciseType.name == exercise_type_name).first()
    )


def delete_exercise_type(db: Session, exercise_type: ExerciseType) -> ExerciseType:
    db.delete(exercise_type),
    db.commit()
    return exercise_type


def update_level(
    db: Session, exercise_type: ExerciseType, update: ExerciseTypeUpdate
) -> ExerciseType:
    exercise_type.name = update.name
    exercise_type.key = update.name.lower().replace(" ", "_")
    db.add(exercise_type)
    db.commit()
    db.refresh(exercise_type)
    return exercise_type
