from gymhero.database.db import get_db
from gymhero.crud import level as level_crud
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status

from sqlalchemy.orm import Session

from gymhero.schemas.level import LevelCreate, LevelInDB, LevelUpdate
from gymhero.log import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=list[LevelInDB], status_code=status.HTTP_200_OK)
def fetch_all_levels(db: Session = Depends(get_db)):
    levels = level_crud.get_all_levels(db)
    return levels


@router.get("/{level_id}", response_model=LevelInDB, status_code=status.HTTP_200_OK)
def fetch_level_by_id(level_id: int, db: Session = Depends(get_db)):
    level = level_crud.get_level_by_id(db, level_id=level_id)

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with id {level_id} not found",
        )

    return level


@router.get(
    "/name/{level_name}", response_model=LevelInDB, status_code=status.HTTP_200_OK
)
def fetch_level_by_name(level_name: str, db: Session = Depends(get_db)):
    level = level_crud.get_level_by_name(db, level_name=level_name)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with name {level_name} not found",
        )
    return level


@router.post("/", response_model=LevelInDB, status_code=status.HTTP_201_CREATED)
def create_level(level: LevelCreate, db: Session = Depends(get_db)):
    level = level_crud.create_level(db, level=level)
    return level


@router.delete("/{level_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_level(level_id: int, db: Session = Depends(get_db)):
    level = level_crud.get_level_by_id(db, level_id=level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with id {level_id} not found. Cannot delete.",
        )
    try:
        level_crud.delete_level(db, level=level)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete level with id {level_id}. Error: {str(e)}",
        )
    return {"detail": f"level with id {level_id} deleted."}


@router.put("/{level_id}", response_model=LevelInDB, status_code=status.HTTP_200_OK)
def update_level(level_id: int, update: LevelUpdate, db: Session = Depends(get_db)):
    level = level_crud.get_level_by_id(db, level_id=level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level with id {level_id} not found. Cannot update.",
        )
    try:
        level = level_crud.update_level(db, level=level, update=update)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update level with id {level_id}. Error: {str(e)}",
        )
    return level
