from gymhero.database.db import get_db
from gymhero.crud import exercise as exercise_crud
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status

from sqlalchemy.orm import Session

from gymhero.schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseInDB,
    ExerciseTypeCreate,
    ExerciseTypeUpdate,
    ExerciseTypeInDB,
)
from gymhero.log import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=list[ExerciseInDB], status_code=status.HTTP_200_OK)
def fetch_all_exercises(db: Session = Depends(get_db)):
    return exercise_crud.get_all_exercises(db)


@router.get(
    "/types/", response_model=list[ExerciseTypeInDB], status_code=status.HTTP_200_OK
)
def fetch_all_exercise_types(db: Session = Depends(get_db)):
    return exercise_crud.get_all_exercise_types(db)


@router.get(
    "/types/{exercise_type_id}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_type_by_id(exercise_type_id: int, db: Session = Depends(get_db)):
    exercise_type = exercise_crud.get_exercise_type_by_id(
        db, exercise_type_id=exercise_type_id
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
    exercise = exercise_crud.get_exercise_by_id(db, exercise_id=exercise_id)
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
    exercise = exercise_crud.get_exercise_by_name(db, exercise_name=exercise_name)
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
    exercise_type = exercise_crud.get_exercise_type_by_name(
        db, exercise_type_name=exercise_type_name
    )
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with name {exercise_type_name} not found",
        )
    return exercise_type


@router.post("/", response_model=ExerciseInDB, status_code=status.HTTP_201_CREATED)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    exercise = exercise_crud.create_exercise(db, exercise=exercise)
    return exercise


@router.post(
    "/types/", response_model=ExerciseTypeInDB, status_code=status.HTTP_201_CREATED
)
def create_exercise_type(
    exercise_type: ExerciseTypeCreate, db: Session = Depends(get_db)
):
    exercise_type = exercise_crud.create_exercise_type(db, exercise_type=exercise_type)
    return exercise_type


@router.put(
    "/{exercise_id}", response_model=ExerciseInDB, status_code=status.HTTP_200_OK
)
def update_exercise(
    exercise_id: int, exercise_update: ExerciseUpdate, db: Session = Depends(get_db)
):
    exercise = exercise_crud.get_exercise_by_id(db, exercise_id=exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    try:
        exercise = exercise_crud.update_exercise(
            db, exercise=exercise, update=exercise_update
        )
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
    exercise_type = exercise_crud.get_exercise_type_by_id(
        db, exercise_type_id=exercise_type_id
    )
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type} not found",
        )
    try:
        exercise_type = exercise_crud.update_exercise_type(
            db, exercise_type=exercise_type, update=exercise_type_update
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update exercise type with id {exercise_type_id}. Error: {str(e)}",
        )
    return exercise_type


@router.delete("/{exercise_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = exercise_crud.get_exercise_by_id(db, exercise_id=exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found. Cannot delete.",
        )
    try:
        exercise_crud.delete_exercise(db, exercise=exercise)
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
    exercise_type = exercise_crud.get_exercise_type_by_id(
        db, exercise_type_id=exercise_type_id
    )
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found. Cannot delete.",
        )
    try:
        exercise_crud.delete_exercise_type(db, exercise_type=exercise_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete exercise type with id {exercise_type_id}. Error: {str(e)}",
        )
    return {"detail": f"exercise type with id {exercise_type_id} deleted."}
