from sqlalchemy.orm import Session

from gymhero.log import get_logger
from gymhero.models.body_part import BodyPart
from gymhero.models.exercise import Exercise, ExerciseType
from gymhero.models.level import Level
from scripts.core.resources import ExerciseRow

log = get_logger(__name__)


def create_levels(session: Session, names: list[str]) -> list[Level]:
    levels = [Level(name=name) for name in names]
    session.add_all(levels)
    session.commit()
    log.debug("Created %d levels", len(levels))
    return levels


def create_body_parts(session: Session, names: list[str]) -> list[BodyPart]:
    body_parts = [BodyPart(name=name) for name in names]
    session.add_all(body_parts)
    session.commit()
    log.debug("Created %d body parts", len(body_parts))
    return body_parts


def create_exercise_types(session: Session, names: list[str]) -> list[ExerciseType]:
    exercise_types = [ExerciseType(name=name) for name in names]
    session.add_all(exercise_types)
    session.commit()
    log.debug("Created %d exercise types", len(exercise_types))
    return exercise_types


def create_exercises(
    session: Session,
    rows: list[ExerciseRow],
    body_part_ids: dict[str, int],
    level_ids: dict[str, int],
    exercise_type_ids: dict[str, int],
    owner_id: int,
) -> list[Exercise]:
    exercises = [
        Exercise(
            name=row["Title"],
            description=row["Desc"],
            target_body_part_id=body_part_ids[row["BodyPart"]],
            exercise_type_id=exercise_type_ids[row["Type"]],
            level_id=level_ids[row["Level"]],
            owner_id=owner_id,
        )
        for row in rows
    ]
    session.add_all(exercises)
    session.commit()
    log.debug("Created %d exercises", len(exercises))
    return exercises
