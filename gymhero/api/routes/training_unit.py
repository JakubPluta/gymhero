from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_pagination_params,
)
from gymhero.crud import training_unit_crud
from gymhero.database.db import get_db
from gymhero.models import TrainingUnit
from gymhero.models.user import User
from gymhero.schemas.common import Page
from gymhero.schemas.exercise import ExerciseInDB
from gymhero.schemas.training_unit import (
    TrainingUnitCreate,
    TrainingUnitInDB,
    TrainingUnitUpdate,
)
from gymhero.services import training_unit as training_unit_service

router = APIRouter()


@router.get(
    "/all",
    response_model=Page[TrainingUnitInDB],
    status_code=status.HTTP_200_OK,
)
async def get_all_training_units(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple[int, int] = Depends(get_pagination_params),
    user: User = Depends(get_current_superuser),
):
    skip, limit = pagination_params
    items = await training_unit_crud.get_many(db, skip=skip, limit=limit)
    total = await training_unit_crud.count(db)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/all/my",
    response_model=Page[TrainingUnitInDB],
    status_code=status.HTTP_200_OK,
)
async def get_all_training_units_for_owner(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple[int, int] = Depends(get_pagination_params),
    user: User = Depends(get_current_active_user),
):
    skip, limit = pagination_params
    items = await training_unit_crud.get_many_for_owner(
        db, owner_id=user.id, skip=skip, limit=limit
    )
    total = await training_unit_crud.count(db, owner_id=user.id)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/{training_unit_id}",
    response_model=TrainingUnitInDB,
    status_code=status.HTTP_200_OK,
)
async def get_training_unit_by_id(
    training_unit_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_unit_service.get_training_unit(
        db, training_unit_id=training_unit_id, actor=user
    )


@router.get(
    "/name/{training_unit_name}",
    response_model=TrainingUnitInDB,
    status_code=status.HTTP_200_OK,
)
async def get_training_unit_by_name(
    training_unit_name: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_unit_service.get_training_unit_by_name(
        db, name=training_unit_name, actor=user
    )


@router.get(
    "/name/{training_unit_name}/superuser",
    response_model=list[TrainingUnitInDB],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_training_units_by_name(
    training_unit_name: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    return await training_unit_crud.get_many(
        db, TrainingUnit.name == training_unit_name
    )


@router.post("/", response_model=TrainingUnitInDB, status_code=status.HTTP_201_CREATED)
async def create_training_unit(
    training_unit_in: TrainingUnitCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_unit_service.create_training_unit(
        db, data=training_unit_in, owner=user
    )


@router.put(
    "/{training_unit_id}",
    response_model=TrainingUnitInDB,
    status_code=status.HTTP_200_OK,
)
async def update_training_unit(
    training_unit_id: int,
    training_unit_update: TrainingUnitUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_unit_service.update_training_unit(
        db, training_unit_id=training_unit_id, data=training_unit_update, actor=user
    )


@router.delete("/{training_unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_unit(
    training_unit_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    await training_unit_service.delete_training_unit(
        db, training_unit_id=training_unit_id, actor=user
    )


@router.put(
    "/{training_unit_id}/exercises/{exercise_id}/add",
    response_model=TrainingUnitInDB,
    status_code=status.HTTP_200_OK,
)
async def add_exercise_to_training_unit(
    training_unit_id: int,
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_unit_service.add_exercise(
        db, training_unit_id=training_unit_id, exercise_id=exercise_id, actor=user
    )


@router.get("/{training_unit_id}/exercises", response_model=list[ExerciseInDB])
async def get_exercises_in_training_unit(
    training_unit_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_unit_service.get_exercises(
        db, training_unit_id=training_unit_id, actor=user
    )


@router.put(
    "/{training_unit_id}/exercises/{exercise_id}/remove",
    response_model=TrainingUnitInDB,
    status_code=status.HTTP_200_OK,
)
async def remove_exercise_from_training_unit(
    training_unit_id: int,
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await training_unit_service.remove_exercise(
        db, training_unit_id=training_unit_id, exercise_id=exercise_id, actor=user
    )
