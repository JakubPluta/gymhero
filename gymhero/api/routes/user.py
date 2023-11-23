from gymhero.api.utils import get_pagination_params
from gymhero.database.db import get_db
from gymhero.crud import user_crud
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status

from sqlalchemy.orm import Session

from gymhero.models import User
from gymhero.schemas.user import (
    UserOut,
    UserCreate,
    UserUpdate,
    UsersInDB,
    UserInDB,
)
from gymhero.log import get_logger


log = get_logger(__name__)


router = APIRouter()


@router.get("/", response_model=UsersInDB, status_code=status.HTTP_200_OK)
def fetch_all_users(
    db: Session = Depends(get_db), pagination_params=Depends(get_pagination_params)
):
    skip, limit = pagination_params
    return user_crud.get_many(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def fetch_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_one(db, User.id == user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with {user_id} not found",
        )
    return user


@router.get("/email/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
def fetch_user_by_email(email: str, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {email} not found"
        )
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=user_create.email)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The user with this {user_create.email} already exists in the system",
        )

    user_in = UserInDB(
        **user_create.model_dump(),
        hashed_password=get_password_hash(user_create.password),
    )
    user = user_crud.create_user(db, user_in)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_one(db, User.id == user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found. Cannot delete.",
        )
    try:
        user_crud.delete(db, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete user with id {user_id}. Error: {str(e)}",
        )


@router.put("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = user_crud.get_one(db, User.id == user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found. Cannot update.",
        )
    try:
        user = user_crud.update(db, user, user_update)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update user with id {user_id}. Error: {str(e)}",
        )
    return user
