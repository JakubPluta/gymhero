"""Training-plan use-cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud import training_plan_crud, training_unit_crud
from gymhero.exceptions import EntityConflictError, EntityNotFoundError
from gymhero.models.training_plan import TrainingPlan
from gymhero.models.training_unit import TrainingUnit
from gymhero.models.user import User
from gymhero.schemas.training_plan import TrainingPlanCreate, TrainingPlanUpdate
from gymhero.services.ownership import get_owned_or_404


async def get_training_plan(
    db: AsyncSession, *, training_plan_id: int, actor: User
) -> TrainingPlan:
    return await _get_owned_or_404(db, training_plan_id, actor)


async def get_training_plan_by_name(
    db: AsyncSession, *, name: str, actor: User
) -> TrainingPlan:
    plan = await training_plan_crud.get_one(
        db, TrainingPlan.name == name, TrainingPlan.owner_id == actor.id
    )
    if plan is None:
        raise EntityNotFoundError(f"Training plan with name {name} not found")
    return plan


async def create_training_plan(
    db: AsyncSession, *, data: TrainingPlanCreate, owner: User
) -> TrainingPlan:
    existing = await training_plan_crud.get_one(
        db, TrainingPlan.name == data.name, TrainingPlan.owner_id == owner.id
    )
    if existing is not None:
        raise EntityConflictError(f"Training plan with name {data.name} already exists")
    return await training_plan_crud.create_with_owner(
        db, obj_create=data, owner_id=owner.id
    )


async def update_training_plan(
    db: AsyncSession, *, training_plan_id: int, data: TrainingPlanUpdate, actor: User
) -> TrainingPlan:
    plan = await _get_owned_or_404(db, training_plan_id, actor)
    return await training_plan_crud.update(db, db_obj=plan, obj_update=data)


async def delete_training_plan(
    db: AsyncSession, *, training_plan_id: int, actor: User
) -> None:
    plan = await _get_owned_or_404(db, training_plan_id, actor)
    await training_plan_crud.delete(db, plan)


async def add_training_unit(
    db: AsyncSession, *, training_plan_id: int, training_unit_id: int, actor: User
) -> TrainingPlan:
    plan = await _get_owned_or_404(db, training_plan_id, actor)
    unit = await _get_unit_or_404(db, training_unit_id)
    updated = await training_plan_crud.add_training_unit_to_training_plan(
        db, training_plan=plan, training_unit=unit
    )
    if updated is None:
        raise EntityConflictError(
            f"Training unit with id {training_unit_id} already exists in training "
            f"plan with id {training_plan_id}"
        )
    return updated


async def remove_training_unit(
    db: AsyncSession, *, training_plan_id: int, training_unit_id: int, actor: User
) -> TrainingPlan:
    plan = await _get_owned_or_404(db, training_plan_id, actor)
    unit = await _get_unit_or_404(db, training_unit_id)
    updated = await training_plan_crud.remove_training_unit_from_training_plan(
        db, training_plan=plan, training_unit=unit
    )
    if updated is None:
        raise EntityConflictError(
            f"Training unit with id {training_unit_id} does not exist in training "
            f"plan with id {training_plan_id}"
        )
    return updated


async def get_training_units(
    db: AsyncSession, *, training_plan_id: int, actor: User
) -> list[TrainingUnit]:
    plan = await _get_owned_or_404(db, training_plan_id, actor)
    return list(plan.training_units)


async def _get_owned_or_404(
    db: AsyncSession, training_plan_id: int, actor: User
) -> TrainingPlan:
    return await get_owned_or_404(
        db,
        crud=training_plan_crud,
        model=TrainingPlan,
        entity_id=training_plan_id,
        actor=actor,
        entity="Training plan",
    )


async def _get_unit_or_404(db: AsyncSession, training_unit_id: int) -> TrainingUnit:
    unit = await training_unit_crud.get_one(db, TrainingUnit.id == training_unit_id)
    if unit is None:
        raise EntityNotFoundError(f"Training unit with id {training_unit_id} not found")
    return unit
