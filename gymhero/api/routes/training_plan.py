from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_pagination_params,
)
from gymhero.crud import training_plan_crud
from gymhero.database.db import get_db
from gymhero.models import TrainingPlan
from gymhero.models.user import User
from gymhero.schemas.common import Page
from gymhero.schemas.training_plan import (
    TrainingPlanCreate,
    TrainingPlanInDB,
    TrainingPlanUpdate,
)
from gymhero.schemas.training_unit import TrainingUnitInDB
from gymhero.services import training_plan as training_plan_service

router = APIRouter()


@router.get(
    "/all",
    response_model=Page[TrainingPlanInDB],
    status_code=status.HTTP_200_OK,
)
async def get_all_training_plans(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple[int, int] = Depends(get_pagination_params),
    user: User = Depends(get_current_superuser),
):
    skip, limit = pagination_params
    items = await training_plan_crud.get_many(db, skip=skip, limit=limit)
    total = await training_plan_crud.count(db)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/all/my",
    response_model=Page[TrainingPlanInDB],
    status_code=status.HTTP_200_OK,
)
async def get_all_training_plans_for_owner(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple[int, int] = Depends(get_pagination_params),
    user: User = Depends(get_current_active_user),
):
    skip, limit = pagination_params
    items = await training_plan_crud.get_many(
        db, TrainingPlan.owner_id == user.id, skip=skip, limit=limit
    )
    total = await training_plan_crud.count(db, TrainingPlan.owner_id == user.id)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/{training_plan_id}",
    response_model=TrainingPlanInDB,
    status_code=status.HTTP_200_OK,
)
async def get_training_plan_by_id(
    training_plan_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_plan_service.get_training_plan(
        db, training_plan_id=training_plan_id, actor=user
    )


@router.get(
    "/name/{training_plan_name}",
    response_model=TrainingPlanInDB,
    status_code=status.HTTP_200_OK,
)
async def get_training_plan_by_name(
    training_plan_name: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_plan_service.get_training_plan_by_name(
        db, name=training_plan_name, actor=user
    )


@router.get(
    "/name/{training_plan_name}/superuser",
    response_model=list[TrainingPlanInDB],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_training_plans_by_name_for_super_user(
    training_plan_name: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    return await training_plan_crud.get_many(
        db, TrainingPlan.name == training_plan_name
    )


@router.post("/", response_model=TrainingPlanInDB, status_code=status.HTTP_201_CREATED)
async def create_training_plan(
    training_plan_create: TrainingPlanCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_plan_service.create_training_plan(
        db, data=training_plan_create, owner=user
    )


@router.delete("/{training_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_plan(
    training_plan_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    await training_plan_service.delete_training_plan(
        db, training_plan_id=training_plan_id, actor=user
    )


@router.put(
    "/{training_plan_id}",
    response_model=TrainingPlanInDB,
    status_code=status.HTTP_200_OK,
)
async def update_training_plan(
    training_plan_id: int,
    training_plan_update: TrainingPlanUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_plan_service.update_training_plan(
        db, training_plan_id=training_plan_id, data=training_plan_update, actor=user
    )


@router.put(
    "/{training_plan_id}/training-units/{training_unit_id}",
    response_model=TrainingPlanInDB,
    status_code=status.HTTP_200_OK,
)
async def add_training_unit_to_training_plan(
    training_plan_id: int,
    training_unit_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_plan_service.add_training_unit(
        db,
        training_plan_id=training_plan_id,
        training_unit_id=training_unit_id,
        actor=user,
    )


@router.delete(
    "/{training_plan_id}/training-units/{training_unit_id}",
    response_model=TrainingPlanInDB,
    status_code=status.HTTP_200_OK,
)
async def remove_training_unit_from_training_plan(
    training_plan_id: int,
    training_unit_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_plan_service.remove_training_unit(
        db,
        training_plan_id=training_plan_id,
        training_unit_id=training_unit_id,
        actor=user,
    )


@router.get(
    "/{training_plan_id}/training-units",
    response_model=list[TrainingUnitInDB],
    status_code=status.HTTP_200_OK,
)
async def get_training_units_in_training_plan(
    training_plan_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_plan_service.get_training_units(
        db, training_plan_id=training_plan_id, actor=user
    )
