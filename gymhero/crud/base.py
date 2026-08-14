"""Async data-access repository. Holds no business rules."""

from typing import Any

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.database.base_class import Base
from gymhero.log import get_logger

type OwnerIDType = int

log = get_logger(__name__)


class CRUDRepository[ModelT: Base]:
    def __init__(self, model: type[ModelT]) -> None:
        self._model = model
        self._name = model.__name__

    async def get_one(
        self, db: AsyncSession, *args: Any, **kwargs: Any
    ) -> ModelT | None:
        stmt = select(self._model).filter(*args).filter_by(**kwargs)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_many(
        self,
        db: AsyncSession,
        *args: Any,
        skip: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> list[ModelT]:
        stmt = (
            select(self._model)
            .filter(*args)
            .filter_by(**kwargs)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def count(self, db: AsyncSession, *args: Any, **kwargs: Any) -> int:
        stmt = (
            select(func.count())
            .select_from(self._model)
            .filter(*args)
            .filter_by(**kwargs)
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    async def create(self, db: AsyncSession, obj_create: BaseModel) -> ModelT:
        obj_create_data = obj_create.model_dump(exclude_none=True, exclude_unset=True)
        db_obj = self._model(**obj_create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelT, obj_update: BaseModel | dict[str, Any]
    ) -> ModelT:
        obj_update_data = (
            obj_update
            if isinstance(obj_update, dict)
            else obj_update.model_dump(exclude_unset=True)
        )
        for field, value in obj_update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ModelT) -> ModelT:
        await db.delete(db_obj)
        await db.commit()
        return db_obj

    async def create_with_owner(
        self, db: AsyncSession, obj_create: BaseModel, owner_id: OwnerIDType
    ) -> ModelT:
        obj_create_data = obj_create.model_dump(
            exclude_none=True, exclude_unset=True, exclude_defaults=True
        )
        db_obj = self._model(**obj_create_data, owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_many_for_owner(
        self,
        db: AsyncSession,
        *args: Any,
        owner_id: OwnerIDType,
        skip: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> list[ModelT]:
        return await self.get_many(
            db, *args, skip=skip, limit=limit, owner_id=owner_id, **kwargs
        )
