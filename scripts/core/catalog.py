from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from gymhero.log import get_logger
from gymhero.models.body_part import BodyPart
from gymhero.models.exercise import Exercise, ExerciseType
from gymhero.models.level import Level
from scripts.core.resources import ExerciseRow

log = get_logger(__name__)


def create_levels(session: Session, names: list[str]) -> list[Level]:
    if names:
        session.execute(
            pg_insert(Level)
            .values([{"name": name} for name in names])
            .on_conflict_do_nothing(index_elements=["name"])
        )
        session.commit()
    levels = list(session.execute(select(Level).where(Level.name.in_(names))).scalars())
    log.debug("Ensured %d levels", len(levels))
    return levels


def create_body_parts(session: Session, names: list[str]) -> list[BodyPart]:
    if names:
        session.execute(
            pg_insert(BodyPart)
            .values([{"name": name} for name in names])
            .on_conflict_do_nothing(index_elements=["name"])
        )
        session.commit()
    body_parts = list(
        session.execute(select(BodyPart).where(BodyPart.name.in_(names))).scalars()
    )
    log.debug("Ensured %d body parts", len(body_parts))
    return body_parts


def create_exercise_types(session: Session, names: list[str]) -> list[ExerciseType]:
    if names:
        session.execute(
            pg_insert(ExerciseType)
            .values([{"name": name} for name in names])
            .on_conflict_do_nothing(index_elements=["name"])
        )
        session.commit()
    exercise_types = list(
        session.execute(
            select(ExerciseType).where(ExerciseType.name.in_(names))
        ).scalars()
    )
    log.debug("Ensured %d exercise types", len(exercise_types))
    return exercise_types


def create_exercises(
    session: Session,
    rows: list[ExerciseRow],
    body_part_ids: dict[str, int],
    level_ids: dict[str, int],
    exercise_type_ids: dict[str, int],
    owner_id: int,
) -> None:
    if not rows:
        return
    session.execute(
        pg_insert(Exercise)
        .values(
            [
                {
                    "name": row["Title"],
                    "description": row["Desc"],
                    "target_body_part_id": body_part_ids[row["BodyPart"]],
                    "exercise_type_id": exercise_type_ids[row["Type"]],
                    "level_id": level_ids[row["Level"]],
                    "owner_id": owner_id,
                }
                for row in rows
            ]
        )
        .on_conflict_do_nothing(index_elements=["name"])
    )
    session.commit()
    log.debug("Ensured %d exercises", len(rows))
