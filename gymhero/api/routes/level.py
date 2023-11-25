from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import level_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models import Level
from gymhero.models.user import User
from gymhero.schemas.level import LevelCreate, LevelInDB, LevelsInDB, LevelUpdate

log = get_logger(__name__)

router = APIRouter()


@router.get("/all", response_model=LevelsInDB, status_code=status.HTTP_200_OK)
def fetch_all_levels(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
):
    skip, limit = pagination_params
    retults = level_crud.get_many(db, skip=skip, limit=limit)
    return LevelsInDB(results=retults)


@router.get(
    "/{level_id}", response_model=Optional[LevelInDB], status_code=status.HTTP_200_OK
)
def fetch_level_by_id(level_id: int, db: Session = Depends(get_db)):
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
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return level_crud.create(db, obj_create=level_create)


@router.delete("/{level_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_level(
    level_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    level = level_crud.get_one(db, Level.id == level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with id {level_id} not found. Cannot delete.",
        )
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
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
    status_code=status.HTTP_201_CREATED,
)
def update_level(
    level_id: int,
    level_update: LevelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    level = level_crud.get_one(db, Level.id == level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with id {level_id} not found. Cannot update.",
        )

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    try:
        level = level_crud.update(db, level, level_update)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update level with id {level_id}. Error: {str(e)}",
        ) from e
    return level
