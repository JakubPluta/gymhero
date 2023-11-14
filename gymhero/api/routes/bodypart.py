from gymhero.database.db import get_db
from gymhero.crud import bodypart as bodypart_exercise
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status

from sqlalchemy.orm import Session

from gymhero.schemas.bodypart import BodyPartUpdate, BodyPartCreate, BodyPartBase, BodyPartInDB
from gymhero.log import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=list[BodyPartInDB], status_code=status.HTTP_200_OK)
def fetch_body_parts(db: Session = Depends(get_db)):
    levels = bodypart_exercise.get_all_body_parts(db)
    return levels


@router.get("/{body_part_id}", response_model=BodyPartInDB, status_code=status.HTTP_200_OK)
def fetch_body_part_by_id(body_part_id: int, db: Session = Depends(get_db)):
    body_part = bodypart_exercise.get_body_part_by_id(db, body_part_id=body_part_id)

    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with id {body_part_id} not found",
        )

    return body_part


@router.get("/name/{body_part_name}", response_model=BodyPartInDB, status_code=status.HTTP_200_OK)
def fetch_body_part_by_id(body_part_name: str, db: Session = Depends(get_db)):
    body_part = bodypart_exercise.get_body_part_by_name(db, body_part_name)
    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with name {body_part_name} not found",
        )
    return body_part


@router.post("/", response_model=BodyPartInDB, status_code=status.HTTP_201_CREATED)
def create_body_part(body_part: BodyPartCreate, db: Session = Depends(get_db)):
    return bodypart_exercise.create_body_part(db, body_part=body_part)


@router.delete("/{body_part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_body_part(body_part_id: int, db: Session = Depends(get_db)):
    bp = bodypart_exercise.get_body_part_by_id(db, body_part_id=body_part_id)
    if bp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with id {body_part_id} not found. Cannot delete.",
        )
    try:
        bodypart_exercise.delete_body_part(db, body_part=bp)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete body part with id {body_part_id}. Error: {str(e)}",
        )
    return {"detail": f"Body part with id {body_part_id} deleted."}

