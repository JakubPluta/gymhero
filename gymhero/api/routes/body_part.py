from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import bodypart_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models import BodyPart
from gymhero.models.user import User
from gymhero.schemas.body_part import BodyPartCreate, BodyPartInDB, BodyPartUpdate

log = get_logger(__name__)

router = APIRouter()


@router.get(
    "/all",
    response_model=List[Optional[BodyPartInDB]],
    status_code=status.HTTP_200_OK,
)
def fetch_body_parts(
    db: Session = Depends(get_db),
    pagination_params: dict = Depends(get_pagination_params),
):
    """
    Fetches the body parts from the database based on pagination parameters.

    Parameters:
        db (Session): The database session.
        pagination_params (dict): The pagination parameters.

    Returns:
        BodyPartsInDB: The fetched body parts from the database.
    """
    skip, limit = pagination_params
    return bodypart_crud.get_many(db, skip=skip, limit=limit)


@router.get(
    "/{body_part_id}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[BodyPartInDB],
)
def fetch_body_part_by_id(body_part_id: int, db: Session = Depends(get_db)):
    """
    Fetches a body part by its ID.

    Parameters:
        body_part_id (int): The ID of the body part to fetch.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        body_part: The fetched body part.

    Raises:
        HTTPException: If the body part with the given ID is not found.
    """
    body_part = bodypart_crud.get_one(db, BodyPart.id == body_part_id)

    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with id {body_part_id} not found",
        )

    return body_part


@router.get(
    "/name/{body_part_name}",
    response_model=Optional[BodyPartInDB],
    status_code=status.HTTP_200_OK,
)
def fetch_body_part_by_name(body_part_name: str, db: Session = Depends(get_db)):
    """
    Fetches a body part from the database by its name.

    Parameters:
        body_part_name (str): The name of the body part.
        db (Session): The database session.

    Returns:
        BodyPartInDB: The body part fetched from the database.

    Raises:
        HTTPException: If the body part with the
        specified name is not found in the database.
    """
    body_part = bodypart_crud.get_one(db, BodyPart.name == body_part_name)
    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with name {body_part_name} not found",
        )
    return body_part


@router.post("/", response_model=BodyPartInDB, status_code=status.HTTP_201_CREATED)
def create_body_part(
    body_part: BodyPartCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
) -> BodyPartInDB:
    """
    Creates a new body part in the database.

    Parameters:
        body_part: The data of the body part to be created.
        db: The database session.
        user: The current superuser.

    Returns:
        The created body part.
    """
    try:
        return bodypart_crud.create(db, obj_create=body_part)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Body part with name {body_part.name} already exists",
        ) from e


@router.delete(
    "/{body_part_id}", status_code=status.HTTP_200_OK, response_model=Dict[str, str]
)
def delete_body_part(
    body_part_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Delete a body part by its ID.

    Parameters:
        body_part_id (int): The ID of the body part to be deleted.
        db (Session): The database session.
        user (User): The current superuser.

    Raises:
        HTTPException: If the body part with the given ID is
        not found or the user does not have permission to delete it.
        HTTPException: If there is an error while deleting the body part.

    Returns:
        dict: A dictionary with a detail message indicating
        that the body part was deleted.
    """
    body_part = bodypart_crud.get_one(db, BodyPart.id == body_part_id)
    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with id {body_part_id} not found. Cannot delete.",
        )
    try:
        bodypart_crud.delete(db, body_part)
    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete body part with id {body_part_id}. Error: {str(e)}",
        ) from e  # pragma: no cover
    return {"detail": f"Body part with id {body_part_id} deleted."}


@router.put(
    "/{body_part_id}",
    response_model=BodyPartInDB,
    status_code=status.HTTP_200_OK,
)
def update_body_part(
    body_part_id: int,
    body_part_update: BodyPartUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Update a body part in the database.

    Parameters:
        body_part_id (int): The ID of the body part to update.
        body_part_update (BodyPartUpdate): The updated body part data.
        db (Session): The database session.
        user (User): The current superuser.

    Raises:
        HTTPException: If the body part with the given ID is not
        found or if the user does not have permission to update the body part.
        HTTPException: If there is an error updating the body part.

    Returns:
        BodyPartInDB: The updated body part.
    """
    body_part = bodypart_crud.get_one(db, BodyPart.id == body_part_id)
    if body_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with id {body_part_id} not found. Cannot update.",
        )

    try:
        body_part = bodypart_crud.update(db, body_part, body_part_update)
    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update body part with id {body_part_id}. Error: {str(e)}",
        ) from e  # pragma: no cover
    return body_part
