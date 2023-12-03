from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from gymhero.api.dependencies import (
    get_current_active_user,
    get_pagination_params,
)
from gymhero.crud import training_unit_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models import TrainingUnit
from gymhero.models.user import User
from gymhero.schemas.training_unit import (
    TrainingUnitCreate,
    TrainingUnitInDB,
    TrainingUnitUpdate,
)

log = get_logger(__name__)

router = APIRouter()


@router.get(
    "/all",
    response_model=List[Optional[TrainingUnitInDB]],
    status_code=status.HTTP_200_OK,
)
def get_all_training_units(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
):
    """
    Retrieves all training units with pagination.

    Parameters:
        db (Session): The database session.
        pagination_params (dict): The pagination parameters.

    Returns:
        TrainingUnitsInDB: The training units retrieved from the database.
    """
    skip, limit = pagination_params
    return training_unit_crud.get_many(db, skip=skip, limit=limit)


@router.get(
    "/all/mine",
    response_model=List[Optional[TrainingUnitInDB]],
    status_code=status.HTTP_200_OK,
)
def get_all_training_units_for_owner(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
    user: User = Depends(get_current_active_user),
):
    """
    Retrieves all training units for the current user with pagination.

    Parameters:
        db (Session): The database session.
        pagination_params (dict): The pagination parameters.
        user (User): The current active user.

    Returns:
        TrainingUnitsInDB: The training units retrieved from the database.
    """
    skip, limit = pagination_params
    return training_unit_crud.get_many_for_owner(
        db, owner_id=user.id, skip=skip, limit=limit
    )


@router.get(
    "/{training_unit_id}",
    response_model=Optional[TrainingUnitInDB],
    status_code=status.HTTP_200_OK,
)
def get_training_unit_by_id(training_unit_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a training unit by ID.

    Parameters:
        training_unit_id (int): The ID of the training unit.
        db (Session): The database session.

    Returns:
        Optional[TrainingUnitInDB]: The training unit retrieved
        from the database, or None if not found.
    """
    training_unit = training_unit_crud.get_one(db, TrainingUnit.id == training_unit_id)
    if training_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training unit with id {training_unit_id} not found",
        )
    return training_unit


@router.get(
    "/name/{training_unit_name}",
    response_model=Optional[TrainingUnitInDB],
    status_code=status.HTTP_200_OK,
)
def get_training_unit_by_name(training_unit_name: str, db: Session = Depends(get_db)):
    """
    Retrieves a training unit by name.

    Parameters:
        training_unit_name (str): The name of the training unit.
        db (Session): The database session.

    Returns:
        Optional[TrainingUnitInDB]: The training unit retrieved
        from the database, or None if not found.
    """
    training_unit = training_unit_crud.get_one(
        db, TrainingUnit.name == training_unit_name
    )
    if training_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training unit with name {training_unit_name} not found",
        )
    return training_unit


@router.post("/", response_model=TrainingUnitInDB, status_code=status.HTTP_201_CREATED)
def create_training_unit(
    training_unit_in: TrainingUnitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Creates a new training unit.

    Parameters:
        training_unit_in (TrainingUnitCreate): The training unit data.
        db (Session): The database session.

    Returns:
        TrainingUnitInDB: The created training unit.
    """
    training_unit = training_unit_crud.create_with_owner(
        db, training_unit_in, owner_id=user.id
    )
    return training_unit


@router.put(
    "/{training_unit_id}",
    response_model=TrainingUnitInDB,
    status_code=status.HTTP_200_OK,
)
def update_training_unit(
    training_unit_id: int,
    training_unit_update: TrainingUnitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Updates a training unit.

    Parameters:
        training_unit_id (int): The ID of the training unit to update.
        training_unit_update (TrainingUnitUpdate): The updated training unit data.
        db (Session): The database session.

    Returns:
        TrainingUnitInDB: The updated training unit.
    """
    training_unit: TrainingUnit = training_unit_crud.get_one(
        db, TrainingUnit.id == training_unit_id
    )
    if training_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training unit with id {training_unit_id} not found",
        )

    if training_unit.owner_id != user.id or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    try:
        training_unit = training_unit_crud.update(
            db, training_unit, training_unit_update
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update training unit. Error: " + str(e),
        ) from e
    return training_unit


@router.delete("/{training_unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_unit(
    training_unit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Deletes a training unit.

    Parameters:
        training_unit_id (int): The ID of the training unit to delete.
        db (Session): The database session.

    Returns:
        Dict[str, str]: A message indicating that the training unit has been deleted.
    """
    training_unit: TrainingUnit = training_unit_crud.get_one(
        db, TrainingUnit.id == training_unit_id
    )
    if training_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training unit with id {training_unit_id} not found",
        )

    if training_unit.owner_id != user.id or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    try:
        training_unit_crud.delete(db, training_unit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete training unit. Error: " + str(e),
        ) from e
    return {"detail": f"Training unit type with id {training_unit_id} deleted."}
