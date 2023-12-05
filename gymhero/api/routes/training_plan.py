from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from gymhero.api.dependencies import get_current_active_user, get_pagination_params
from gymhero.crud import training_plan_crud, training_unit_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models import TrainingPlan
from gymhero.models.training_unit import TrainingUnit
from gymhero.models.user import User
from gymhero.schemas.training_plan import (
    TrainingPlanCreate,
    TrainingPlanInDB,
    TrainingPlanUpdate,
)

log = get_logger(__name__)

router = APIRouter()


@router.get(
    "/all",
    response_model=List[Optional[TrainingPlanInDB]],
    status_code=status.HTTP_200_OK,
)
def get_all_training_plans(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
):
    """
    Retrieves all training plans with pagination.

    Parameters:
        db (Session): The database session.
        pagination_params (dict): A dictionary containing the pagination parameters.

    Returns:
        List[Optional[TrainingPlanInDB]]: A list of
        training plans retrieved from the database.
    """
    skip, limit = pagination_params
    return training_plan_crud.get_many(db, skip=skip, limit=limit)


@router.get(
    "/all/mine",
    response_model=List[Optional[TrainingPlanInDB]],
    status_code=status.HTTP_200_OK,
)
def get_all_training_plans_for_owner(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
    user: User = Depends(get_current_active_user),
):
    """
    Retrieve all training plans for the owner.

    Parameters:
        db (Session): The database session.
        pagination_params (dict): The pagination parameters.
        user (User): The current active user.

    Returns:
        List[Optional[TrainingPlanInDB]]: A list of training plans owned by the user.
    """
    skip, limit = pagination_params
    return training_plan_crud.get_many_for_owner(
        db, skip=skip, limit=limit, owner_id=user.id
    )


@router.get(
    "/{training_plan_id}",
    response_model=Optional[TrainingPlanInDB],
    status_code=status.HTTP_200_OK,
)
def get_training_plan_by_id(training_plan_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a training plan from the database by its ID.

    Parameters:
        training_plan_id (int): The ID of the training plan to retrieve.
        db (Session): The database session.

    Returns:
        Optional[TrainingPlanInDB]: The retrieved training plan, or None if not found.

    Raises:
        HTTPException: If the training plan with the specified ID is not found.

    """
    training_plan = training_plan_crud.get_one(db, TrainingPlan.id == training_plan_id)
    if training_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan with id {training_plan_id} not found",
        )
    return training_plan


@router.get(
    "/name/{training_plan_name}",
    response_model=Optional[TrainingPlanInDB],
    status_code=status.HTTP_200_OK,
)
def get_training_plan_by_name(training_plan_name: str, db: Session = Depends(get_db)):
    """
    Get a training plan by its name.

    Parameters:
        training_plan_name (str): The name of the training plan.
        db (Session): The database session.

    Returns:
        Optional[TrainingPlanInDB]: The training plan with the specified name,
        if found. Otherwise, None.

    Raises:
        HTTPException: If the training plan with the specified name is not found.

    """

    training_plan = training_plan_crud.get_one(
        db, TrainingPlan.name == training_plan_name
    )
    if training_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan with name {training_plan_name} not found",
        )
    return training_plan


@router.post(
    "/", response_model=Optional[TrainingPlanInDB], status_code=status.HTTP_201_CREATED
)
def create_training_plan(
    training_plan_create: TrainingPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Create a new training plan with the specified data.

    Parameters:
        training_plan_create (TrainingPlanCreate):
            The data for creating the training plan.
        db (Session, optional): The database session.
            Defaults to Depends(get_db).
        user (User, optional): The current authenticated user.

    Returns:
        Optional[TrainingPlanInDB]: The created training plan.

    Raises:
        HTTPException: If there is an error creating the training plan.
    """
    return training_plan_crud.create_with_owner(
        db, obj_create=training_plan_create, owner_id=user.id
    )


@router.delete(
    "/{training_plan_id}", response_model=dict, status_code=status.HTTP_200_OK
)
def delete_training_plan(
    training_plan_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Deletes a training plan with the given `training_plan_id`.

    Parameters:
        training_plan_id (int): The ID of the training plan to be deleted.
        db (Session, optional): The database session.
        user (User, optional): The current active user.

    Raises:
        HTTPException: If the training plan is not found
            or the user does not have enough privileges.
        Exception: If there is an error while deleting the training plan.

    Returns:
        None
    """
    training_plan: TrainingPlan = training_plan_crud.get_one(
        db, TrainingPlan.id == training_plan_id
    )
    if training_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan with id {training_plan_id} not found. \
            Cannot delete.",
        )
    if not user.is_superuser or training_plan.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    try:
        training_plan_crud.delete(db, training_plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return


@router.put(
    "/{training_plan_id}",
    response_model=Optional[TrainingPlanInDB],
    status_code=status.HTTP_201_CREATED,
)
def update_training_plan(
    training_plan_id: int,
    training_plan_update: TrainingPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Update a training plan with the given ID.

    Parameters:
        training_plan_id (int): The ID of the training plan to update.
        training_plan_update (TrainingPlanUpdate): The updated training plan data.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        user (User, optional): The current user.

    Returns:
        Optional[TrainingPlanInDB]: The updated training plan.

    Raises:
        HTTPException 404: If the training plan with the given ID is not found.
        HTTPException 403: If the user does not have sufficient privileges.
    """
    training_plan: TrainingPlan = training_plan_crud.get_one(
        db, TrainingPlan.id == training_plan_id
    )
    if training_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan with id {training_plan_id} not found. \
            Cannot update.",
        )
    if not user.is_superuser or training_plan.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return training_plan_crud.update(
        db, db_obj=training_plan, obj_update=training_plan_update
    )


@router.put(
    "/{training_plan_id}/training_units/{training_unit_id}/add",
)
def add_training_unit_to_training_plan(
    training_plan_id: int,
    training_unit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Add a training unit to a training plan.

    Parameters:
        training_plan_id (int): The ID of the training plan to add the training unit to.
        training_unit_id (int): The ID of the training unit to add to the training plan.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        user (User, optional): The current user.

    Returns:
        None

    Raises:
        HTTPException 404: If the training plan or
            training unit with the given IDs are not found.
        HTTPException 403: If the user does not have sufficient privileges.
    """
    training_plan: TrainingPlan = training_plan_crud.get_one(
        db, TrainingPlan.id == training_plan_id
    )
    if training_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan with id {training_plan_id} not found. \
            Cannot update.",
        )
    training_unit = training_unit_crud.get_one(db, TrainingUnit.id == training_unit_id)
    if training_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training unit with id {training_unit_id} not found. \
            Cannot update.",
        )
    if not user.is_superuser or training_plan.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    training_plan = training_plan_crud.add_training_unit_to_training_plan(
        db, training_plan=training_plan, training_unit=training_unit
    )
    return training_plan


@router.put(
    "/{training_plan_id}/training_units/{training_unit_id}/remove",
)
def remove_training_unit_from_training_plan(
    training_plan_id: int,
    training_unit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Remove a training unit from a training plan.

    Parameters:
        training_plan_id (int): The ID of the training plan to
        remove the training unit from.
        training_unit_id (int): The ID of the training unit to
        remove from the training plan.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        user (User, optional): The current user.

    Returns:
        None

    Raises:
        HTTPException 404: If the training plan or training unit
        with the given IDs are not found.
        HTTPException 403: If the user does not have sufficient privileges.
    """
    training_plan: TrainingPlan = training_plan_crud.get_one(
        db, TrainingPlan.id == training_plan_id
    )
    if training_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan with id {training_plan_id} not found. \
            Cannot update.",
        )
    training_unit = training_unit_crud.get_one(db, TrainingUnit.id == training_unit_id)
    if training_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training unit with id {training_unit_id} not found. \
            Cannot update.",
        )
    if not user.is_superuser or training_plan.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return training_plan_crud.remove_training_unit_from_training_plan(
        db, training_plan=training_plan, training_unit=training_unit
    )


@router.get(
    "/{training_plan_id}/training_units",
)
def get_training_units_in_training_plan(
    training_plan_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Get all training units in a training plan.

    Parameters:
        training_plan_id (int): The ID of the training plan
        to get the training units from.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        user (User, optional): The current user.

    Returns:
        List[TrainingUnit]: A list of training units in the training plan.

    Raises:
        HTTPException 404: If the training plan with the given ID is not found.
        HTTPException 403: If the user does not have sufficient privileges.
    """
    training_plan: TrainingPlan = training_plan_crud.get_one(
        db, TrainingPlan.id == training_plan_id
    )
    if training_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan with id {training_plan_id} not found. ",
        )
    if not user.is_superuser or training_plan.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )

    return training_plan.training_units
