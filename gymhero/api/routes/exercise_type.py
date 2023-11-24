from gymhero.database.db import get_db
from gymhero.crud import exercise_type_crud
from gymhero.api.dependencies import get_pagination_params
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status

from sqlalchemy.orm import Session
from gymhero.models.exercise import ExerciseType
from gymhero.schemas.exercise import (
    ExerciseTypeCreate,
    ExerciseTypeUpdate,
    ExerciseTypeInDB,
    ExerciseTypesInDB,
)
from gymhero.log import get_logger


log = get_logger(__name__)

router = APIRouter()


@router.get("/types/", response_model=ExerciseTypesInDB, status_code=status.HTTP_200_OK)
def fetch_all_exercise_types(
    db: Session = Depends(get_db), pagination_params=Depends(get_pagination_params)
):
    """
    Fetches all exercise types from the database.

    Args:
        - db (Session): The database session.
        - pagination_params (Tuple[int, int]): The pagination args (skip, limit).

    Returns:
        - List[ExerciseTypesInDB]: A list of exercise types from the database.
    """
    skip, limit = pagination_params
    return exercise_type_crud.get_many(db, skip=skip, limit=limit)


@router.get(
    "/types/{exercise_type_id}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_type_by_id(exercise_type_id: int, db: Session = Depends(get_db)):
    """
    Fetches an exercise type by its ID from the database.

    Args:
        exercise_type_id (int): The ID of the exercise type to fetch.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        ExerciseTypeInDB: The fetched exercise type.

    Raises:
        HTTPException: If the exercise type with the given ID is not found in the database.
    """
    exercise_type = exercise_type_crud.get_one(db, ExerciseType.id == exercise_type_id)
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found",
        )
    return exercise_type


@router.get(
    "/types/name/{exercise_type_name}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_type_by_name(exercise_type_name: str, db: Session = Depends(get_db)):
    """
    Fetches an exercise type from the database by its name.

    Args:
        - exercise_type_name (str): The name of the exercise type to fetch.
        - db (Session): The database session.

    Returns:
        - ExerciseTypeInDB: The exercise type fetched from the database.

    Raises:
        - HTTPException: If the exercise type with the given name is not found.
    """
    exercise_type = exercise_type_crud.get_one(
        db, ExerciseType.name == exercise_type_name
    )
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with name {exercise_type_name} not found",
        )
    return exercise_type


@router.post(
    "/types/",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_201_CREATED,
)
def create_exercise_type(
    exercise_type_create: ExerciseTypeCreate,
    db: Session = Depends(get_db),
):
    """
    Creates a new exercise type.

    Args:
        exercise_type_create (ExerciseTypeCreate): The exercise type data to create.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        ExerciseTypeInDB: The newly created exercise type.
    """
    exercise_type = exercise_type_crud.create(db, exercise_type_create)
    return exercise_type


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
    """
    Update an exercise type in the database.

    Args:
        exercise_type_id (int): The ID of the exercise type to be updated.
        exercise_type_update (ExerciseTypeUpdate): The updated exercise type data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        ExerciseTypeInDB: The updated exercise type.

    Raises:
        HTTPException: If the exercise type with the specified ID is not found or if there is an internal server error during the update process.
    """
    exercise_type = exercise_type_crud.get_one(db, ExerciseType.id == exercise_type_id)
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found",
        )
    try:
        exercise_type = exercise_type_crud.update_exercise_type(
            db, exercise_type, exercise_type_update
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update exercise type with id {exercise_type_id}. Error: {str(e)}",
        )
    return exercise_type


@router.delete(
    "/types/{exercise_type_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
def delete_exercise_type(exercise_type_id: int, db: Session = Depends(get_db)):
    """
    Deletes an exercise type with the given exercise_type_id.

    Args:
        exercise_type_id (int): The ID of the exercise type to delete.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary with a detail message indicating whether the
              exercise type was successfully deleted or not.
    """
    exercise_type = exercise_type_crud.get_one(db, ExerciseType.id == exercise_type_id)
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found. Cannot delete.",
        )
    try:
        exercise_type_crud.delete(db, exercise_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete exercise type with id {exercise_type_id}. Error: {str(e)}",
        )
    return {"detail": f"Exercise type with id {exercise_type_id} deleted."}
