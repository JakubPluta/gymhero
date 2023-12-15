from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import exercise_type_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models.exercise import ExerciseType
from gymhero.models.user import User
from gymhero.schemas.exercise_type import (
    ExerciseTypeCreate,
    ExerciseTypeInDB,
    ExerciseTypeUpdate,
)

log = get_logger(__name__)

router = APIRouter()


@router.get(
    "/all",
    response_model=List[Optional[ExerciseTypeInDB]],
    status_code=status.HTTP_200_OK,
)
def fetch_all_exercise_types(
    db: Session = Depends(get_db), pagination_params=Depends(get_pagination_params)
):
    """
    Fetches all exercise types from the database.

    Parameters:
        db (Session): The database session.
        pagination_params (Tuple[int, int]): The pagination args (skip, limit).

    Returns:
        List[ExerciseTypesInDB]: A list of exercise types from the database.
    """
    skip, limit = pagination_params
    return exercise_type_crud.get_many(db, skip=skip, limit=limit)


@router.get(
    "/{exercise_type_id}",
    response_model=Optional[ExerciseTypeInDB],
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_type_by_id(exercise_type_id: int, db: Session = Depends(get_db)):
    """
    Fetches an exercise type by its ID from the database.

    Parameters:
        exercise_type_id (int): The ID of the exercise type to fetch.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        ExerciseTypeInDB: The fetched exercise type.

    Raises:
        HTTPException: If the exercise type with the given
        ID is not found in the database.
    """
    exercise_type = exercise_type_crud.get_one(db, ExerciseType.id == exercise_type_id)
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found",
        )
    return exercise_type


@router.get(
    "/name/{exercise_type_name}",
    response_model=Optional[ExerciseTypeInDB],
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_type_by_name(exercise_type_name: str, db: Session = Depends(get_db)):
    """
    Fetches an exercise type from the database by its name.

    Parameters:
        exercise_type_name (str): The name of the exercise type to fetch.
        db (Session): The database session.

    Returns:
        ExerciseTypeInDB: The exercise type fetched from the database.

    Raises:
        HTTPException: If the exercise type with the given name is not found.
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
    "/",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_201_CREATED,
)
def create_exercise_type(
    exercise_type_create: ExerciseTypeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Creates a new exercise type.

    Parameters:
        exercise_type_create (ExerciseTypeCreate): The exercise type data to create.
        db (Session): The database session. Defaults to Depends(get_db).
        user (User): The current user.

    Returns:
        ExerciseTypeInDB: The newly created exercise type.
    """
    try:
        exercise_type = exercise_type_crud.create(db, exercise_type_create)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Exercise type with name {exercise_type_create.name} already exists",
        ) from e
    return exercise_type


@router.put(
    "/{exercise_type_id}",
    response_model=ExerciseTypeInDB,
    status_code=status.HTTP_200_OK,
)
def update_exercise_type(
    exercise_type_id: int,
    exercise_type_update: ExerciseTypeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Update an exercise type in the database.

    Parameters:
        exercise_type_id (int): The ID of the exercise type to be updated.
        exercise_type_update (ExerciseTypeUpdate): The updated exercise type data.
        db (Session): The database session. Defaults to Depends(get_db).
        user (User): The current user.

    Returns:
        ExerciseTypeInDB: The updated exercise type.

    Raises:
        HTTPException: If the exercise type with the specified ID
        is not found or if there is an internal server error during the update process.
    """
    exercise_type = exercise_type_crud.get_one(db, ExerciseType.id == exercise_type_id)
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found.",
        )

    try:
        exercise_type = exercise_type_crud.update(
            db, exercise_type, exercise_type_update
        )
    except Exception as e:  # pragma no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update exercise type with id {exercise_type_id}. \
                Error: {str(e)}",
        ) from e  # pragma no cover
    return exercise_type


@router.delete(
    "/{exercise_type_id}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str],
)
def delete_exercise_type(
    exercise_type_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Deletes an exercise type with the given exercise_type_id.

    Parameters:
        exercise_type_id (int): The ID of the exercise type to delete.
        db (Session): The database session. Defaults to Depends(get_db).
        user (User): The current user.

    Returns:
        dict: A dictionary with a detail message indicating whether the
              exercise type was successfully deleted or not.
    """
    exercise_type = exercise_type_crud.get_one(db, ExerciseType.id == exercise_type_id)
    if exercise_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise type with id {exercise_type_id} not found.",
        )
    try:
        exercise_type_crud.delete(db, exercise_type)
    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete exercise type with id {exercise_type_id}. \
                Error: {str(e)}",
        ) from e  # pragma: no cover
    return {"detail": f"Exercise type with id {exercise_type_id} deleted."}
