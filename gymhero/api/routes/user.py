from gymhero.database.db import get_db
from gymhero.crud import user as user_crud
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status

from sqlalchemy.orm import Session

from gymhero.schemas.user import (
    UserInDB,
    UserOut,
    UserBase,
    UserCreate,
    UserUpdate,
    UserUpdateDB,
)
from gymhero.log import get_logger


log = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=list[UserOut], status_code=status.HTTP_200_OK)
def fetch_all_users(db: Session = Depends(get_db)):
    users = user_crud.get_all_users(db)
    return users

@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def fetch_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {user_id} not found")
    return user

@router.get("/email/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
def fetch_user_by_email(email: str, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {email} not found")
    return user


@router.post(
    "/", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=user_create.email)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The user with this {user_create.email} already exists in the system",
        )

    user_in = UserInDB(**user_create.model_dump(), hashed_password=get_password_hash(user_create.password))
    user = user_crud.create_user(db, user=user_in)
    return user

