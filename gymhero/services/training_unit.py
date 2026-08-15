"""Training-unit use-cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud import exercise_crud, training_unit_crud
from gymhero.exceptions import EntityConflictError, EntityNotFoundError
from gymhero.models.exercise import Exercise
from gymhero.models.training_unit import TrainingUnit
from gymhero.models.user import User
from gymhero.schemas.training_unit import TrainingUnitCreate, TrainingUnitUpdate
from gymhero.services.ownership import get_owned_or_404


async def get_training_unit(
    db: AsyncSession, *, training_unit_id: int, actor: User
) -> TrainingUnit:
    return await _get_owned_or_404(db, training_unit_id, actor)


async def get_training_unit_by_name(
    db: AsyncSession, *, name: str, actor: User
) -> TrainingUnit:
    unit = await training_unit_crud.get_one(
        db, TrainingUnit.name == name, TrainingUnit.owner_id == actor.id
    )
    if unit is None:
        raise EntityNotFoundError(f"Training unit with name {name} not found")
    return unit


async def create_training_unit(
    db: AsyncSession, *, data: TrainingUnitCreate, owner: User
) -> TrainingUnit:
    existing = await training_unit_crud.get_one(
        db, TrainingUnit.name == data.name, TrainingUnit.owner_id == owner.id
    )
    if existing is not None:
        raise EntityConflictError(f"Training unit with name {data.name} already exists")
    return await training_unit_crud.create_with_owner(db, data, owner_id=owner.id)


async def update_training_unit(
    db: AsyncSession, *, training_unit_id: int, data: TrainingUnitUpdate, actor: User
) -> TrainingUnit:
    unit = await _get_owned_or_404(db, training_unit_id, actor)
    return await training_unit_crud.update(db, unit, data)


async def delete_training_unit(
    db: AsyncSession, *, training_unit_id: int, actor: User
) -> None:
    unit = await _get_owned_or_404(db, training_unit_id, actor)
    await training_unit_crud.delete(db, unit)


async def add_exercise(
    db: AsyncSession, *, training_unit_id: int, exercise_id: int, actor: User
) -> TrainingUnit:
    unit = await _get_owned_or_404(db, training_unit_id, actor)
    exercise = await _get_exercise_or_404(db, exercise_id)
    updated = await training_unit_crud.add_exercise_to_training_unit(db, unit, exercise)
    if updated is None:
        raise EntityConflictError(
            f"Exercise with id {exercise_id} already exists in training unit "
            f"with id {training_unit_id}"
        )
    return updated


async def remove_exercise(
    db: AsyncSession, *, training_unit_id: int, exercise_id: int, actor: User
) -> TrainingUnit:
    unit = await _get_owned_or_404(db, training_unit_id, actor)
    exercise = await _get_exercise_or_404(db, exercise_id)
    try:
        return await training_unit_crud.remove_exercise_from_training_unit(
            db, unit, exercise
        )
    except ValueError as exc:
        raise EntityConflictError(
            f"Exercise with id {exercise_id} not found in training unit "
            f"with id {training_unit_id}"
        ) from exc


async def get_exercises(
    db: AsyncSession, *, training_unit_id: int, actor: User
) -> list[Exercise]:
    unit = await _get_owned_or_404(db, training_unit_id, actor)
    return training_unit_crud.get_exercises_in_training_unit(unit)


async def _get_owned_or_404(
    db: AsyncSession, training_unit_id: int, actor: User
) -> TrainingUnit:
    return await get_owned_or_404(
        db,
        crud=training_unit_crud,
        model=TrainingUnit,
        entity_id=training_unit_id,
        actor=actor,
        entity="Training unit",
    )


async def _get_exercise_or_404(db: AsyncSession, exercise_id: int) -> Exercise:
    exercise = await exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise EntityNotFoundError(f"Exercise with id {exercise_id} not found")
    return exercise
