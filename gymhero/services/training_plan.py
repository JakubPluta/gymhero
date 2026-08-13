"""Training-plan use-cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.authorization import authorize_owner_or_superuser
from gymhero.crud import training_plan_crud, training_unit_crud
from gymhero.exceptions import EntityConflictError, EntityNotFoundError
from gymhero.models.training_plan import TrainingPlan
from gymhero.models.training_unit import TrainingUnit
from gymhero.models.user import User
from gymhero.schemas.training_plan import TrainingPlanCreate, TrainingPlanUpdate


async def get_training_plan(
    db: AsyncSession, *, training_plan_id: int, actor: User
) -> TrainingPlan:
    # Non-superusers only ever see their own plans.
    if actor.is_superuser:
        plan = await training_plan_crud.get_one(db, TrainingPlan.id == training_plan_id)
    else:
        plan = await training_plan_crud.get_one(
            db, TrainingPlan.id == training_plan_id, owner_id=actor.id
        )
    if plan is None:
        raise EntityNotFoundError(f"Training plan with id {training_plan_id} not found")
    return plan


async def get_training_plan_by_name(
    db: AsyncSession, *, name: str, actor: User
) -> TrainingPlan:
    plan = await training_plan_crud.get_one(
        db, TrainingPlan.name == name, owner_id=actor.id
    )
    if plan is None:
        raise EntityNotFoundError(f"Training plan with name {name} not found")
    return plan


async def create_training_plan(
    db: AsyncSession, *, data: TrainingPlanCreate, owner: User
) -> TrainingPlan:
    existing = await training_plan_crud.get_one(
        db, TrainingPlan.name == data.name, owner_id=owner.id
    )
    if existing is not None:
        raise EntityConflictError(f"Training plan with name {data.name} already exists")
    return await training_plan_crud.create_with_owner(
        db, obj_create=data, owner_id=owner.id
    )


async def update_training_plan(
    db: AsyncSession, *, training_plan_id: int, data: TrainingPlanUpdate, actor: User
) -> TrainingPlan:
    plan = await _get_or_404(db, training_plan_id, suffix="Cannot update.")
    authorize_owner_or_superuser(plan, actor)
    return await training_plan_crud.update(db, db_obj=plan, obj_update=data)


async def delete_training_plan(
    db: AsyncSession, *, training_plan_id: int, actor: User
) -> None:
    plan = await _get_or_404(db, training_plan_id, suffix="Cannot delete.")
    authorize_owner_or_superuser(plan, actor)
    await training_plan_crud.delete(db, plan)


async def add_training_unit(
    db: AsyncSession, *, training_plan_id: int, training_unit_id: int, actor: User
) -> TrainingPlan:
    plan = await _get_or_404(db, training_plan_id, suffix="Cannot update.")
    unit = await _get_unit_or_404(db, training_unit_id)
    authorize_owner_or_superuser(plan, actor)
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
    plan = await _get_or_404(db, training_plan_id, suffix="Cannot update.")
    authorize_owner_or_superuser(plan, actor)
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
    plan = await _get_or_404(db, training_plan_id)
    authorize_owner_or_superuser(plan, actor)
    return plan.training_units


async def _get_or_404(
    db: AsyncSession, training_plan_id: int, *, suffix: str | None = None
) -> TrainingPlan:
    plan = await training_plan_crud.get_one(db, TrainingPlan.id == training_plan_id)
    if plan is None:
        message = f"Training plan with id {training_plan_id} not found"
        raise EntityNotFoundError(f"{message}. {suffix}" if suffix else message)
    return plan


async def _get_unit_or_404(db: AsyncSession, training_unit_id: int) -> TrainingUnit:
    unit = await training_unit_crud.get_one(db, TrainingUnit.id == training_unit_id)
    if unit is None:
        raise EntityNotFoundError(
            f"Training unit with id {training_unit_id} not found. Cannot update."
        )
    return unit
