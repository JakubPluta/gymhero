from gymhero.database.db import get_db
from gymhero.crud import exercise_crud, exercise_type_crud
from gymhero.api.dependencies import get_pagination_params, get_current_active_user, get_current_superuser
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status

from sqlalchemy.orm import Session

from gymhero.models import User
from gymhero.models.exercise import ExerciseType, Exercise
from gymhero.schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseInDB,
    ExerciseTypeCreate,
    ExerciseTypeUpdate,
    ExerciseTypeInDB,
    ExercisesInDB,
    ExerciseTypesInDB,
)
from gymhero.log import get_logger


log = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=ExercisesInDB, status_code=status.HTTP_200_OK)
def fetch_all_exercises(
    db: Session = Depends(get_db), pagination_params=Depends(get_pagination_params)
):
    skip, limit = pagination_params
    return exercise_crud.get_many(db, skip=skip, limit=limit)


@router.get("/types/", response_model=ExerciseTypesInDB, status_code=status.HTTP_200_OK)
def fetch_all_exercise_types(
    db: Session = Depends(get_db), pagination_params=Depends(get_pagination_params)
):
    skip, limit = pagination_params
    return exercise_type_crud.get_many(db, skip=skip, limit=limit)


@router.get(
    "/types/{exercise_type_id}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_type_by_id(exercise_type_id: int, db: Session = Depends(get_db)):
    exercise_type = exercise_type_crud.get_one(
        db, ExerciseType.id == exercise_type_id
    )
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found",
        )
    return exercise_type


@router.get(
    "/{exercise_id}", response_model=ExerciseInDB, status_code=status.HTTP_200_OK
)
def fetch_exercise_by_id(exercise_id: int, db: Session = Depends(get_db)):
    exercise = exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    return exercise


@router.get(
    "/name/{exercise_name}", response_model=ExerciseInDB, status_code=status.HTTP_200_OK
)
def fetch_exercise_by_name(exercise_name: str, db: Session = Depends(get_db)):
    exercise = exercise_crud.get_one(db, Exercise.name == exercise_name)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with name {exercise_name} not found",
        )
    return exercise


@router.get(
    "/types/name/{exercise_type_name}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_type_by_name(exercise_type_name: str, db: Session = Depends(get_db)):
    exercise_type = exercise_type_crud.get_one(
        db, ExerciseType.name == exercise_type_name
    )
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with name {exercise_type_name} not found",
        )
    return exercise_type


@router.post("/", response_model=ExerciseInDB, status_code=status.HTTP_201_CREATED)
def create_exercise(exercise_create: ExerciseCreate, db: Session = Depends(get_db),
                    user: User = Depends(get_current_active_user)):

    exercise = exercise_crud.create_with_owner(db, exercise_create, owner_id=user.id)
    return exercise


@router.post(
    "/types/", response_model=ExerciseTypeInDB, status_code=status.HTTP_201_CREATED
)
def create_exercise_type(
    exercise_type_create: ExerciseTypeCreate, db: Session = Depends(get_db)
):
    exercise_type = exercise_type_crud.create(db, exercise_type_create)
    return exercise_type


@router.put(
    "/{exercise_id}", response_model=ExerciseInDB, status_code=status.HTTP_200_OK
)
def update_exercise(
    exercise_id: int, exercise_update: ExerciseUpdate, db: Session = Depends(get_db)
):
    exercise = exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    try:
        exercise = exercise_crud.update(db, exercise, exercise_update)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update exercise with id {exercise_id}. Error: {str(e)}",
        )
    return exercise


@router.put(
    "/types/{exercise_type_id}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
def update_exercise_type(
    exercise_type_id: int,
    exercise_type_update: ExerciseTypeUpdate,
    db: Session = Depends(get_db),
):
    exercise_type = exercise_type_crud.get_one(
        db, ExerciseType.id == exercise_type_id
    )
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type} not found",
        )
    try:
        exercise_type = exercise_crud.update_exercise_type(
            db, exercise_type, exercise_type_update
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update exercise type with id {exercise_type_id}. Error: {str(e)}",
        )
    return exercise_type


@router.delete("/{exercise_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found. Cannot delete.",
        )
    try:
        exercise_crud.delete(db, exercise)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete exercise with id {exercise_id}. Error: {str(e)}",
        )
    return {"detail": f"exercise with id {exercise_id} deleted."}


@router.delete(
    "/types/{exercise_type_id}", status_code=status.HTTP_200_OK, response_model=dict
)
def delete_exercise_type(exercise_type_id: int, db: Session = Depends(get_db)):
    exercise_type = exercise_type_crud.get_one(
        db, ExerciseType.id == exercise_type_id
    )
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found. Cannot delete.",
        )
    try:
        exercise_crud.delete(db, exercise_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete exercise type with id {exercise_type_id}. Error: {str(e)}",
        )
    return {"detail": f"exercise type with id {exercise_type_id} deleted."}
