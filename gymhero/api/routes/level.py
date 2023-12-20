from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import level_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models import Level
from gymhero.models.user import User
from gymhero.schemas.level import LevelCreate, LevelInDB, LevelUpdate

log = get_logger(__name__)

router = APIRouter()


@router.get(
    "/all", response_model=List[Optional[LevelInDB]], status_code=status.HTTP_200_OK
)
def fetch_all_levels(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
):
    """
    Fetches all levels from the database with pagination.

    Parameters:
        db (Session): The database session.
        pagination_params (dict): The pagination parameters.
            - skip (int): The number of records to skip.
            - limit (int): The maximum number of records to fetch.

    Returns:
        results (List[Optional[LevelInDB]]): A list of level
        objects fetched from the database.
    """
    skip, limit = pagination_params
    results = level_crud.get_many(db, skip=skip, limit=limit)
    return results


@router.get(
    "/{level_id}", response_model=Optional[LevelInDB], status_code=status.HTTP_200_OK
)
def fetch_level_by_id(level_id: int, db: Session = Depends(get_db)):
    """
    Fetches a level by its ID.

    Parameters:
        level_id (int): The ID of the level to fetch.
        db (Session): The database session.
        Defaults to the result of the `get_db` function.

    Returns:
        Optional[LevelInDB]: The fetched level, or None if not found.
    """
    level = level_crud.get_one(db, Level.id == level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with id {level_id} not found",
        )
    return level


@router.get(
    "/name/{level_name}",
    response_model=Optional[LevelInDB],
    status_code=status.HTTP_200_OK,
)
def fetch_level_by_name(level_name: str, db: Session = Depends(get_db)):
    """
    Fetches a level from the database by its name.

    Parameters:
        level_name (str): The name of the level to fetch.
        db (Session): The database session.

    Returns:
        Optional[LevelInDB]: The fetched level, or None if it doesn't exist.
    """
    level = level_crud.get_one(db, Level.name == level_name)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with name {level_name} not found",
        )
    return level


@router.post(
    "/", response_model=Optional[LevelInDB], status_code=status.HTTP_201_CREATED
)
def create_level(
    level_create: LevelCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """Creates a new level in the database.

    Parameters:
        level_create (LevelCreate): The data required to create a new level.
        db (Session): The database session.
        user (User): The current superuser making the request.

    Returns:
        Optional[LevelInDB]: The newly created level if successful.

    Raises:
        HTTPException: If the user is not a superuser or if
        there is an error creating the level.
    """
    try:
        return level_crud.create(db, obj_create=level_create)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't create level. Level with name: {level_create.name} already exists",
        ) from e

    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't create level. Error: {str(e)}",
        ) from e  # pragma: no cover


@router.delete("/{level_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_level(
    level_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Deletes a level from the database.

    Parameters:
        level_id (int): The ID of the level to be deleted.
        db (Session): The database session.
            Defaults to Depends(get_db).
        user (User): The current superuser.

    Raises:
        HTTPException: If the level with the specified ID is not found
        or the user does not have enough privileges.
        HTTPException: If there is an error while deleting the level.

    Returns:
        dict: A dictionary with the detail
        message indicating that the level was deleted.
    """
    level = level_crud.get_one(db, Level.id == level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with id {level_id} not found. Cannot delete.",
        )
    try:
        level_crud.delete(db, level)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete level with id {level_id}. Error: {str(e)}",
        ) from e
    return {"detail": f"level with id {level_id} deleted."}


@router.put(
    "/{level_id}",
    response_model=Optional[LevelInDB],
    status_code=status.HTTP_200_OK,
)
def update_level(
    level_id: int,
    level_update: LevelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Update a level in the database.

    Parameters:
        level_id (int): The ID of the level to be updated.
        level_update (LevelUpdate): The updated level data.
        db (Session): The database session.
        user (User): The current user.

    Returns:
        Optional[LevelInDB]: The updated level, if successful.
    """
    level = level_crud.get_one(db, Level.id == level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with id {level_id} not found. Cannot update.",
        )
    try:
        level = level_crud.update(db, level, level_update)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update level with id {level_id}. Error: {str(e)}",
        ) from e
    return level
