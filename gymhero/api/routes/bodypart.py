from gymhero.api.utils import get_pagination_params
from gymhero.database.db import get_db
from gymhero.crud import bodypart_crud
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status

from sqlalchemy.orm import Session

from gymhero.models import BodyPart
from gymhero.schemas.body_part import (
    BodyPartUpdate,
    BodyPartCreate,
    BodyPartInDB,
    BodyPartsInDB,
)
from gymhero.log import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=BodyPartsInDB, status_code=status.HTTP_200_OK)
def fetch_body_parts(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
):
    skip, limit = pagination_params
    return bodypart_crud.get_many_records(db, skip=skip, limit=limit)


@router.get(
    "/{body_part_id}", response_model=BodyPartInDB, status_code=status.HTTP_200_OK
)
def fetch_body_part_by_id(body_part_id: int, db: Session = Depends(get_db)):
    body_part = bodypart_crud.get_one_record(db, BodyPart.id == body_part_id)

    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with id {body_part_id} not found",
        )

    return body_part


@router.get(
    "/name/{body_part_name}",
    response_model=BodyPartInDB,
    status_code=status.HTTP_200_OK,
)
def fetch_body_part_by_id(body_part_name: str, db: Session = Depends(get_db)):
    body_part = bodypart_crud.get_one_record(db, BodyPart.name == body_part_name)
    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with name {body_part_name} not found",
        )
    return body_part


@router.post("/", response_model=BodyPartInDB, status_code=status.HTTP_201_CREATED)
def create_body_part(body_part: BodyPartCreate, db: Session = Depends(get_db)):
    return bodypart_crud.create_record(db, obj_create=body_part)


@router.delete("/{body_part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_body_part(body_part_id: int, db: Session = Depends(get_db)):
    bp = bodypart_crud.get_one_record(db, BodyPart.id == body_part_id)
    if bp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with id {body_part_id} not found. Cannot delete.",
        )
    try:
        bodypart_crud.delete(db, bp)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete body part with id {body_part_id}. Error: {str(e)}",
        )
    return {"detail": f"Body part with id {body_part_id} deleted."}


@router.put(
    "/{body_part_id}", response_model=BodyPartInDB, status_code=status.HTTP_201_CREATED
)
def update_body_part(
    body_part_id: int, body_part_update: BodyPartUpdate, db: Session = Depends(get_db)
):
    body_part = bodypart_crud.get_one_record(db, BodyPart.id == body_part_id)
    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with id {body_part_id} not found. Cannot update.",
        )
    try:
        body_part = bodypart_crud.update_record(db, body_part, body_part_update)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update body part with id {body_part_id}. Error: {str(e)}",
        )
    return body_part
