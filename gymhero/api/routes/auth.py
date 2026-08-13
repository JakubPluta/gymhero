from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero import security
from gymhero.crud import user_crud
from gymhero.database import get_db
from gymhero.models import User
from gymhero.schemas.auth import RefreshRequest, Token, UserRegister
from gymhero.schemas.common import Message
from gymhero.schemas.user import UserInDB

router = APIRouter()


def _token_pair(user_id: int) -> dict[str, str]:
    return {
        "access_token": security.create_access_token(subject=user_id),
        "refresh_token": security.create_refresh_token(subject=user_id),
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, Any]:
    user = await user_crud.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    if not user_crud.is_active_user(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return _token_pair(user.id)


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    body: RefreshRequest, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
    )
    try:
        payload = security.decode_token(body.refresh_token, expected_type="refresh")
    except jwt.InvalidTokenError as e:
        raise invalid from e

    user = await user_crud.get_one(db, User.id == int(payload["sub"]))
    if user is None or not user_crud.is_active_user(user):
        raise invalid
    return _token_pair(user.id)


@router.post("/register", response_model=Message, status_code=status.HTTP_201_CREATED)
async def register(user_register: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_email(db, email=user_register.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The user with this {user_register.email} already exists in the system",
        )

    user_in = UserInDB(
        **user_register.model_dump(exclude={"password"}, exclude_unset=True),
        hashed_password=security.get_password_hash(
            user_register.password.get_secret_value()
        ),
    )
    await user_crud.create(db, user_in)
    return {"message": "User created successfully"}
