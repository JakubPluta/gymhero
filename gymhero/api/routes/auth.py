from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from gymhero import security
from gymhero.config import settings
from gymhero.crud import user_crud
from gymhero.database import get_db
from gymhero.schemas.auth import Token, UserRegister
from gymhero.schemas.user import UserInDB

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, Any]:
    """
    Endpoint for user login. Authenticates the user using the provided
    email and password.

    Parameters:
        - db (Session): The database session.
        - form_data (OAuth2PasswordRequestForm): The form data
        containing the username and password.

    Returns:
        - Dict[str, Any]: A dictionary containing the access token and token type.
    """
    user = user_crud.authenticate_user(
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

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(user_register: UserRegister, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=user_register.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The user with this {user_register.email} already exists in the system",
        )

    user_in = UserInDB(
        **user_register.model_dump(exclude_unset=True, exclude_defaults=True),
        hashed_password=security.get_password_hash(user_register.password),
    )

    user_crud.create(db, user_in)
    return {"message": "User created successfully"}
