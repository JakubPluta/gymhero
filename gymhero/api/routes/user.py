from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import user_crud
from gymhero.database.db import get_db
from gymhero.models import User
from gymhero.schemas.common import Page
from gymhero.schemas.user import UserCreate, UserOut, UserUpdate
from gymhero.services import user as user_service

router = APIRouter(dependencies=[Depends(get_current_superuser)])


@router.get("/all", response_model=Page[UserOut], status_code=status.HTTP_200_OK)
async def fetch_all_users(
    db: AsyncSession = Depends(get_db),
    pagination_params: tuple = Depends(get_pagination_params),
):
    skip, limit = pagination_params
    items = await user_crud.get_many(db, skip=skip, limit=limit)
    total = await user_crud.count(db)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def fetch_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_service.get_user(db, user_id=user_id)


@router.get("/email/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def fetch_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    return await user_service.get_user_by_email(db, email=email)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, data=user_create)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    await user_service.delete_user(db, user_id=user_id, actor=current_user)


@router.put("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)
):
    return await user_service.update_user(db, user_id=user_id, data=user_update)
