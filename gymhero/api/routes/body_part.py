from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import bodypart_crud
from gymhero.database.db import get_db
from gymhero.models import BodyPart
from gymhero.models.user import User
from gymhero.schemas.body_part import BodyPartCreate, BodyPartInDB, BodyPartUpdate
from gymhero.schemas.common import Page
from gymhero.services import reference

router = APIRouter()

_ENTITY = "Body part"


@router.get(
    "/all",
    response_model=Page[BodyPartInDB],
    status_code=status.HTTP_200_OK,
)
async def fetch_body_parts(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple = Depends(get_pagination_params),
):
    skip, limit = pagination_params
    items = await bodypart_crud.get_many(db, skip=skip, limit=limit)
    total = await bodypart_crud.count(db)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/{body_part_id}",
    status_code=status.HTTP_200_OK,
    response_model=BodyPartInDB | None,
)
async def fetch_body_part_by_id(body_part_id: int, db: AsyncSession = Depends(get_db)):
    return await reference.get_by_id_or_404(
        db, crud=bodypart_crud, model=BodyPart, entity_id=body_part_id, entity=_ENTITY
    )


@router.get(
    "/name/{body_part_name}",
    response_model=BodyPartInDB | None,
    status_code=status.HTTP_200_OK,
)
async def fetch_body_part_by_name(
    body_part_name: str, db: AsyncSession = Depends(get_db)
):
    return await reference.get_by_name_or_404(
        db, crud=bodypart_crud, model=BodyPart, name=body_part_name, entity=_ENTITY
    )


@router.post("/", response_model=BodyPartInDB, status_code=status.HTTP_201_CREATED)
async def create_body_part(
    body_part: BodyPartCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    return await reference.create_unique(
        db, crud=bodypart_crud, data=body_part, entity=_ENTITY
    )


@router.delete("/{body_part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_body_part(
    body_part_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    await reference.delete_by_id(
        db,
        crud=bodypart_crud,
        model=BodyPart,
        entity_id=body_part_id,
        entity=_ENTITY,
        not_found_suffix=". Cannot delete.",
    )


@router.put(
    "/{body_part_id}", response_model=BodyPartInDB, status_code=status.HTTP_200_OK
)
async def update_body_part(
    body_part_id: int,
    body_part_update: BodyPartUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    return await reference.update_by_id(
        db,
        crud=bodypart_crud,
        model=BodyPart,
        entity_id=body_part_id,
        data=body_part_update,
        entity=_ENTITY,
        not_found_suffix=". Cannot update.",
    )
