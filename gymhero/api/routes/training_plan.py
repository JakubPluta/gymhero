from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from gymhero.api.dependencies import (
    get_current_active_user,
    get_pagination_params,
)
from gymhero.crud import training_plan_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models import TrainingPlan
from gymhero.models.user import User
from gymhero.schemas.training_plan import (
    TrainingPlanCreate,
    TrainingPlanInDB,
    TrainingPlansInDB,
    TrainingPlanUpdate,
)

log = get_logger(__name__)

router = APIRouter()


@router.get("/all", response_model=TrainingPlansInDB, status_code=status.HTTP_200_OK)
def get_all_training_plans(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
):
    skip, limit = pagination_params
    results = training_plan_crud.get_many(db, skip=skip, limit=limit)
    return TrainingPlansInDB(results=results)


@router.get(
    "/all/mine", response_model=TrainingPlansInDB, status_code=status.HTTP_200_OK
)
def get_all_training_plans_for_owner(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
    user: User = Depends(get_current_active_user),
):
    skip, limit = pagination_params
    results = training_plan_crud.get_many_for_owner(
        db, skip=skip, limit=limit, owner_id=user.id
    )
    return TrainingPlansInDB(results=results)


@router.get(
    "/{training_plan_id}",
    response_model=Optional[TrainingPlanInDB],
    status_code=status.HTTP_200_OK,
)
def get_training_plan_by_id(training_plan_id: int, db: Session = Depends(get_db)):
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
