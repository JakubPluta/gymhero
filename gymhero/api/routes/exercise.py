from typing import Annotated, List, Optional, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from gymhero.api.dependencies import get_current_active_user, get_pagination_params
from gymhero.crud import exercise_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models import User
from gymhero.models.exercise import Exercise
from gymhero.schemas.exercise import ExerciseCreate, ExerciseInDB, ExerciseUpdate

log = get_logger(__name__)

router = APIRouter()


@router.get(
    "/all", response_model=List[Optional[ExerciseInDB]], status_code=status.HTTP_200_OK
)
def fetch_all_exercises(
    db: Session = Depends(get_db),
    pagination_params: Tuple[int, int] = Depends(get_pagination_params),
) -> List[Optional[ExerciseInDB]]:
    """
    Fetch all exercises.

    This function fetches all exercises from the
    database based on the pagination parameters.

    Parameters:
        db (Session): The database session.
        pagination_params (Tuple[int, int]): The pagination parameters (skip, limit).

    Returns:
        ExercisesInDB: The list of exercises fetched from the database.
    """
    skip, limit = pagination_params
    return exercise_crud.get_many(db, skip=skip, limit=limit)


@router.get(
    "/my", response_model=List[Optional[ExerciseInDB]], status_code=status.HTTP_200_OK
)
def fetch_all_exercises_for_owner(
    db: Session = Depends(get_db),
    pagination_params: Tuple[int, int] = Depends(get_pagination_params),
    user: User = Depends(get_current_active_user),
) -> List[Optional[ExerciseInDB]]:
    """
    Fetches all exercises for user

    Parameters:
        db (Session): The database session.
        pagination_params (Tuple[int, int]): The pagination parameters (skip, limit).
        user (User): The current active user.

    Returns:
        ExercisesInDB: The exercises fetched for the owner.
    """
    skip, limit = pagination_params
    return exercise_crud.get_many_for_owner(
        db, skip=skip, limit=limit, owner_id=user.id
    )


@router.get(
    "/{exercise_id}",
    response_model=Optional[ExerciseInDB],
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_by_id(
    exercise_id: int, db: Session = Depends(get_db)
) -> ExerciseInDB:
    """
    Fetches an exercise by its ID.

    Parameters:
        exercise_id (int): The ID of the exercise.
        db (Session): The database session.

    Returns:
        ExerciseInDB: The fetched exercise.

    Raises:
        HTTPException: If the exercise is not found.
    """
    exercise = exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    return exercise


@router.get(
    "/name/{exercise_name}",
    response_model=ExerciseInDB,
    status_code=status.HTTP_200_OK,
)
def fetch_exercise_by_name(exercise_name: str, db: Session = Depends(get_db)):
    """
    Fetches an exercise by its name from the database.

    Parameters:
        exercise_name (str): The name of the exercise.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        ExerciseInDB: The exercise retrieved from the database.

    Raises:
        HTTPException: If the exercise with the given name is not found in the database.
    """
    exercise = exercise_crud.get_one(db, Exercise.name == exercise_name)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with name {exercise_name} not found",
        )
    return exercise


@router.post(
    "/",
    response_model=ExerciseInDB,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
def create_exercise(
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
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Create an exercise.

    Parameters:
        exercise_create (ExerciseCreate): The exercise data to be created.
        db (Session, optional): The database session.
            Defaults to Depends(get_db).
        user (User, optional): The current active user.


    Returns:
        ExerciseInDB: The created exercise.

    """
    try:
        exercise = exercise_crud.create_with_owner(
            db, exercise_create, owner_id=user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Exercise with name {exercise_create.name} already exists",
        ) from e
    return exercise


@router.put(
    "/{exercise_id}",
    response_model=ExerciseInDB,
    status_code=status.HTTP_200_OK,
)
def update_exercise(
    exercise_id: int,
    exercise_update: ExerciseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Update an exercise by its ID.

    Parameters:
        exercise_id (int): The ID of the exercise to be updated.
        exercise_update (ExerciseUpdate): The updated exercise data.
        db (Session, optional): The database session.
            Defaults to Depends(get_db).
        user (User, optional): The current authenticated user.


    Returns:
        ExerciseInDB: The updated exercise.

    Raises:
        HTTPException: If the exercise does not exist or
            the user does not have enough permissions.
        HTTPException: If there is an error updating
            the exercise in the database.
    """
    exercise = exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )

    if exercise.owner_id != user.id or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update exercise",
        )

    try:
        exercise = exercise_crud.update(db, exercise, exercise_update)
    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update exercise with id {exercise_id}. Error: {str(e)}",
        ) from e  # pragma: no cover
    return exercise


@router.delete("/{exercise_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Deletes an exercise by its ID.

    Parameters:
        exercise_id (int): The ID of the exercise to delete.
        db (Session): The database session.
        user (User): The current user.

    Returns:
        dict: A dictionary containing the detail that
            the exercise with the given ID was deleted.

    Raises:
        HTTPException: If the exercise with the given ID is not found.
        HTTPException: If the user does not have enough
            permissions to delete the exercise.
        HTTPException: If there is an error while
            deleting the exercise from the database.
    """
    exercise = exercise_crud.get_one(db, Exercise.id == exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found. Cannot delete.",
        )

    if exercise.owner_id != user.id or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete exercise",
        )

    try:
        exercise_crud.delete(db, exercise)
    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete exercise with id {exercise_id}. Error: {str(e)}",
        ) from e  # pragma: no cover

    return {"detail": f"Exercise with id {exercise_id} deleted."}
