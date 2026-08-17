from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.dependencies import get_current_active_user, get_pagination_params
from gymhero.database.db import get_db
from gymhero.models import User
from gymhero.schemas.common import Page
from gymhero.schemas.exercise import ExerciseCreate, ExerciseInDB, ExerciseUpdate
from gymhero.services import exercise as exercise_service

router = APIRouter()


@router.get("/all", response_model=Page[ExerciseInDB], status_code=status.HTTP_200_OK)
async def fetch_all_exercises(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple[int, int] = Depends(get_pagination_params),
    q: str | None = Query(None),
    exercise_type_id: int | None = Query(None),
    level_id: int | None = Query(None),
    target_body_part_id: int | None = Query(None),
    user: User = Depends(get_current_active_user),
):
    skip, limit = pagination_params
    items, total = await exercise_service.list_exercises(
        db,
        q=q,
        exercise_type_id=exercise_type_id,
        level_id=level_id,
        target_body_part_id=target_body_part_id,
        skip=skip,
        limit=limit,
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/my", response_model=Page[ExerciseInDB], status_code=status.HTTP_200_OK)
async def fetch_all_exercises_for_owner(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple[int, int] = Depends(get_pagination_params),
    q: str | None = Query(None),
    exercise_type_id: int | None = Query(None),
    level_id: int | None = Query(None),
    target_body_part_id: int | None = Query(None),
    user: User = Depends(get_current_active_user),
):
    skip, limit = pagination_params
    items, total = await exercise_service.list_exercises(
        db,
        owner_id=user.id,
        q=q,
        exercise_type_id=exercise_type_id,
        level_id=level_id,
        target_body_part_id=target_body_part_id,
        skip=skip,
        limit=limit,
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/{exercise_id}",
    response_model=ExerciseInDB,
    status_code=status.HTTP_200_OK,
)
async def fetch_exercise_by_id(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await exercise_service.get_exercise(db, exercise_id)


@router.get(
    "/name/{exercise_name}",
    response_model=ExerciseInDB,
    status_code=status.HTTP_200_OK,
)
async def fetch_exercise_by_name(
    exercise_name: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await exercise_service.get_exercise_by_name(db, exercise_name)


@router.post(
    "/",
    response_model=ExerciseInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_exercise(
    exercise_create: Annotated[
        ExerciseCreate,
        Body(
            examples=[
                {
                    "name": "Bench Press with closed eyes",
                    "target_body_part_id": 1,
                    "exercise_type_id": 1,
                    "level_id": 1,
                    "description": "description",
                }
            ]
        ),
    ],
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await exercise_service.create_exercise(db, data=exercise_create, owner=user)


@router.patch(
    "/{exercise_id}",
    response_model=ExerciseInDB,
    status_code=status.HTTP_200_OK,
)
async def update_exercise(
    exercise_id: int,
    exercise_update: ExerciseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await exercise_service.update_exercise(
        db, exercise_id=exercise_id, data=exercise_update, actor=user
    )


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    await exercise_service.delete_exercise(db, exercise_id=exercise_id, actor=user)
