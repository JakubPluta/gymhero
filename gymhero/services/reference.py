"""Generic helpers for name-keyed reference resources (Level/BodyPart/ExerciseType)."""

from typing import Protocol

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud.base import CRUDRepository
from gymhero.database.base_class import Base
from gymhero.exceptions import EntityConflictError, EntityNotFoundError


class _NamedCreateSchema(Protocol):
    name: str


async def get_by_id_or_404[ModelT: Base](
    db: AsyncSession,
    *,
    crud: CRUDRepository[ModelT],
    model: type[ModelT],
    entity_id: int,
    entity: str,
    not_found_suffix: str = "",
) -> ModelT:
    # `model.id` is a mapped column resolved at runtime (no static SA plugin here).
    obj = await crud.get_one(db, model.id == entity_id)  # type: ignore[attr-defined]
    if obj is None:
        raise EntityNotFoundError(
            f"{entity} with id {entity_id} not found{not_found_suffix}"
        )
    return obj


async def get_by_name_or_404[ModelT: Base](
    db: AsyncSession,
    *,
    crud: CRUDRepository[ModelT],
    model: type[ModelT],
    name: str,
    entity: str,
) -> ModelT:
    obj = await crud.get_one(db, model.name == name)  # type: ignore[attr-defined]
    if obj is None:
        raise EntityNotFoundError(f"{entity} with name {name} not found")
    return obj


async def create_unique[ModelT: Base](
    db: AsyncSession,
    *,
    crud: CRUDRepository[ModelT],
    data: _NamedCreateSchema,
    entity: str,
) -> ModelT:
    try:
        # data is a pydantic Create model at runtime; the Protocol only pins `name`.
        return await crud.create(db, data)  # type: ignore[arg-type]
    except IntegrityError as exc:
        await db.rollback()  # failed unique-constraint commit poisons the session
        raise EntityConflictError(
            f"{entity} with name {data.name} already exists"
        ) from exc


async def update_by_id[ModelT: Base](
    db: AsyncSession,
    *,
    crud: CRUDRepository[ModelT],
    model: type[ModelT],
    entity_id: int,
    data: BaseModel,
    entity: str,
    not_found_suffix: str = "",
) -> ModelT:
    obj = await get_by_id_or_404(
        db,
        crud=crud,
        model=model,
        entity_id=entity_id,
        entity=entity,
        not_found_suffix=not_found_suffix,
    )
    return await crud.update(db, obj, data)


async def delete_by_id[ModelT: Base](
    db: AsyncSession,
    *,
    crud: CRUDRepository[ModelT],
    model: type[ModelT],
    entity_id: int,
    entity: str,
    not_found_suffix: str = "",
) -> None:
    obj = await get_by_id_or_404(
        db,
        crud=crud,
        model=model,
        entity_id=entity_id,
        entity=entity,
        not_found_suffix=not_found_suffix,
    )
    await crud.delete(db, obj)
