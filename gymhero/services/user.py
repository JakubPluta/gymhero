"""User administration use-cases (superuser-only)."""

from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud import user_crud
from gymhero.exceptions import (
    EntityConflictError,
    EntityNotFoundError,
    PermissionDeniedError,
)
from gymhero.models.user import User
from gymhero.schemas.user import UserCreate, UserInDB, UserUpdate
from gymhero.security import get_password_hash


async def get_user(
    db: AsyncSession, *, user_id: int, not_found_suffix: str = ""
) -> User:
    user = await user_crud.get_one(db, User.id == user_id)
    if user is None:
        raise EntityNotFoundError(f"User with id {user_id} not found{not_found_suffix}")
    return user


async def get_user_by_email(db: AsyncSession, *, email: str) -> User:
    user = await user_crud.get_user_by_email(db, email=email)
    if user is None:
        raise EntityNotFoundError(f"User with email {email} not found")
    return user


async def create_user(db: AsyncSession, *, data: UserCreate) -> User:
    if await user_crud.get_user_by_email(db, email=data.email) is not None:
        raise EntityConflictError(f"User with email {data.email} already exists")
    user_in = UserInDB(
        **data.model_dump(),
        hashed_password=get_password_hash(data.password),
    )
    return await user_crud.create(db, user_in)


async def update_user(db: AsyncSession, *, user_id: int, data: UserUpdate) -> User:
    user = await get_user(db, user_id=user_id, not_found_suffix=". Cannot update.")
    return await user_crud.update(db, user, data)


async def delete_user(db: AsyncSession, *, user_id: int, actor: User) -> None:
    user = await get_user(db, user_id=user_id, not_found_suffix=". Cannot delete.")
    if user.id == actor.id:
        raise PermissionDeniedError("You cannot delete yourself")
    await user_crud.delete(db, user)
