from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import level_crud
from gymhero.database.db import get_db
from gymhero.models import Level
from gymhero.models.user import User
from gymhero.schemas.common import Page
from gymhero.schemas.level import LevelCreate, LevelInDB, LevelUpdate
from gymhero.services import reference

router = APIRouter()

_ENTITY = "Level"


@router.get("/all", response_model=Page[LevelInDB], status_code=status.HTTP_200_OK)
async def fetch_all_levels(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple = Depends(get_pagination_params),
):
    skip, limit = pagination_params
    items = await level_crud.get_many(db, skip=skip, limit=limit)
    total = await level_crud.count(db)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/{level_id}", response_model=LevelInDB | None, status_code=status.HTTP_200_OK
)
async def fetch_level_by_id(level_id: int, db: AsyncSession = Depends(get_db)):
    return await reference.get_by_id_or_404(
        db, crud=level_crud, model=Level, entity_id=level_id, entity=_ENTITY
    )


@router.get(
    "/name/{level_name}",
    response_model=LevelInDB | None,
    status_code=status.HTTP_200_OK,
)
async def fetch_level_by_name(level_name: str, db: AsyncSession = Depends(get_db)):
    return await reference.get_by_name_or_404(
        db, crud=level_crud, model=Level, name=level_name, entity=_ENTITY
    )


@router.post("/", response_model=LevelInDB | None, status_code=status.HTTP_201_CREATED)
async def create_level(
    level_create: LevelCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    return await reference.create_unique(
        db, crud=level_crud, data=level_create, entity=_ENTITY
    )


@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_level(
    level_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    await reference.delete_by_id(
        db,
        crud=level_crud,
        model=Level,
        entity_id=level_id,
        entity=_ENTITY,
        not_found_suffix=". Cannot delete.",
    )


@router.put(
    "/{level_id}", response_model=LevelInDB | None, status_code=status.HTTP_200_OK
)
async def update_level(
    level_id: int,
    level_update: LevelUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    return await reference.update_by_id(
        db,
        crud=level_crud,
        model=Level,
        entity_id=level_id,
        data=level_update,
        entity=_ENTITY,
        not_found_suffix=". Cannot update.",
    )
