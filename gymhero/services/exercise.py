"""Exercise use-cases."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.authorization import authorize_owner_or_superuser
from gymhero.crud import exercise_crud
from gymhero.exceptions import EntityConflictError, EntityNotFoundError
from gymhero.models.exercise import Exercise
from gymhero.models.user import User
from gymhero.schemas.exercise import ExerciseCreate, ExerciseUpdate


async def get_exercise(db: AsyncSession, exercise_id: int) -> Exercise:
    exercise = await exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise EntityNotFoundError(f"Exercise with id {exercise_id} not found")
    return exercise


async def get_exercise_by_name(db: AsyncSession, name: str) -> Exercise:
    exercise = await exercise_crud.get_one(db, Exercise.name == name)
    if exercise is None:
        raise EntityNotFoundError(f"Exercise with name {name} not found")
    return exercise


async def create_exercise(
    db: AsyncSession, *, data: ExerciseCreate, owner: User
) -> Exercise:
    if await exercise_crud.get_one(db, Exercise.name == data.name) is not None:
        raise EntityConflictError(f"Exercise with name {data.name} already exists")
    try:
        return await exercise_crud.create_with_owner(db, data, owner_id=owner.id)
    except IntegrityError as exc:  # concurrent insert of the same name
        await db.rollback()
        raise EntityConflictError(
            f"Exercise with name {data.name} already exists"
        ) from exc


async def update_exercise(
    db: AsyncSession, *, exercise_id: int, data: ExerciseUpdate, actor: User
) -> Exercise:
    exercise = await get_exercise(db, exercise_id)
    authorize_owner_or_superuser(
        exercise, actor, message="Not enough permissions to update exercise"
    )
    return await exercise_crud.update(db, exercise, data)


async def delete_exercise(db: AsyncSession, *, exercise_id: int, actor: User) -> None:
    exercise = await exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise EntityNotFoundError(
            f"Exercise with id {exercise_id} not found. Cannot delete."
        )
    authorize_owner_or_superuser(
        exercise, actor, message="Not enough permissions to delete exercise"
    )
    await exercise_crud.delete(db, exercise)
