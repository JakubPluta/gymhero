from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import exercise_type_crud
from gymhero.database.db import get_db
from gymhero.models.exercise import ExerciseType
from gymhero.models.user import User
from gymhero.schemas.common import Page
from gymhero.schemas.exercise_type import (
    ExerciseTypeCreate,
    ExerciseTypeInDB,
    ExerciseTypeUpdate,
)
from gymhero.services import reference

router = APIRouter()

_ENTITY = "Exercise type"


@router.get(
    "/all",
    response_model=Page[ExerciseTypeInDB],
    status_code=status.HTTP_200_OK,
)
async def fetch_all_exercise_types(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple[int, int] = Depends(get_pagination_params),
):
    skip, limit = pagination_params
    items = await exercise_type_crud.get_many(db, skip=skip, limit=limit)
    total = await exercise_type_crud.count(db)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/{exercise_type_id}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
async def fetch_exercise_type_by_id(
    exercise_type_id: int, db: AsyncSession = Depends(get_db)
):
    return await reference.get_by_id_or_404(
        db,
        crud=exercise_type_crud,
        model=ExerciseType,
        entity_id=exercise_type_id,
        entity=_ENTITY,
    )


@router.get(
    "/name/{exercise_type_name}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
async def fetch_exercise_type_by_name(
    exercise_type_name: str, db: AsyncSession = Depends(get_db)
):
    return await reference.get_by_name_or_404(
        db,
        crud=exercise_type_crud,
        model=ExerciseType,
        name=exercise_type_name,
        entity=_ENTITY,
    )


@router.post("/", response_model=ExerciseTypeInDB, status_code=status.HTTP_201_CREATED)
async def create_exercise_type(
    exercise_type_create: ExerciseTypeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    return await reference.create_unique(
        db, crud=exercise_type_crud, data=exercise_type_create, entity=_ENTITY
    )


@router.put(
    "/{exercise_type_id}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
async def update_exercise_type(
    exercise_type_id: int,
    exercise_type_update: ExerciseTypeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    return await reference.update_by_id(
        db,
        crud=exercise_type_crud,
        model=ExerciseType,
        entity_id=exercise_type_id,
        data=exercise_type_update,
        entity=_ENTITY,
        not_found_suffix=".",
    )


@router.delete("/{exercise_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise_type(
    exercise_type_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    await reference.delete_by_id(
        db,
        crud=exercise_type_crud,
        model=ExerciseType,
        entity_id=exercise_type_id,
        entity=_ENTITY,
        not_found_suffix=".",
    )
