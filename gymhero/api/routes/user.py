from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from gymhero.api.dependencies import get_current_superuser, get_pagination_params
from gymhero.crud import user_crud
from gymhero.database.db import get_db
from gymhero.log import get_logger
from gymhero.models import User
from gymhero.schemas.user import UserCreate, UserInDB, UserOut, UserUpdate
from gymhero.security import get_password_hash

log = get_logger(__name__)


router = APIRouter(dependencies=[Depends(get_current_superuser)])


@router.get(
    "/all", response_model=List[Optional[UserOut]], status_code=status.HTTP_200_OK
)
def fetch_all_users(
    db: Session = Depends(get_db), pagination_params=Depends(get_pagination_params)
):
    """
    Fetches all users with pagination.

    Parameters:
        db (Session): The database session.
        pagination_params (Tuple[int, int]): A tuple with
            the skip and limit values for pagination.

    Returns:
        List[Optional[UserOut]]: A list of user objects,
            or None if there are no users.

    Raises:
        None
    """
    skip, limit = pagination_params
    return user_crud.get_many(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def fetch_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Fetches a user by their ID from the database.

    Parameters:
        user_id (int): The ID of the user to fetch.
        db (Session): The database session.

    Returns:
        UserOut: The user object fetched from the database.

    Raises:
        HTTPException: If the user with the specified ID is not found in the database.
    """
    user = user_crud.get_one(db, User.id == user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with {user_id} not found",
        )
    return user


@router.get("/email/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
def fetch_user_by_email(email: str, db: Session = Depends(get_db)):
    """
    Fetches a user from the database based on the provided email.

    Parameters:
        email (str): The email address of the user.
        db (Session, optional): The database session.
        Defaults to the result of calling `get_db`.

    Returns:
        UserOut: The user object fetched from the database.

    Raises:
        HTTPException: If no user is found with the provided email,
            an HTTP 404 Not Found exception is raised.
    """
    user = user_crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {email} not found"
        )
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Create a new user.

    Parameters:
        user_create (UserCreate): The user data to be created.
        db (Session): The database session.
        user (User): The current superuser.

    Returns:
        User: The newly created user.

    Raises:
        HTTPException: If a user with the same email already exists in the system.
    """
    user = user_crud.get_user_by_email(db, email=user_create.email)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The user with this {user_create.email} already exists \
            in the system",
        )
    user_in = UserInDB(
        **user_create.model_dump(),
        hashed_password=get_password_hash(user_create.password),
    )
    user = user_crud.create(db, user_in)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Delete a user by user ID.

    Parameters:
        user_id (int): The ID of the user to delete.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The current authenticated superuser.

    Raises:
        HTTPException: If the user is not found or the user tries to delete themselves.
        HTTPException: If there is an error deleting the user.

    Returns:
        None

    """
    user = user_crud.get_one(db, User.id == user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found. Cannot delete.",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete yourself",
        )
    try:
        user_crud.delete(db, user)
    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete user with id {user_id}. Error: {str(e)}",
        ) from e  # pragma: no cover

    return {"detail": f"User with id {user_id} deleted."}


@router.put("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Update a user with the given ID.

    Parameters:
        user_id (int): The ID of the user to update.
        user_update (UserUpdate): The updated user information.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        user (User, optional): The current superuser.

    Returns:
        UserOut: The updated user information.

    Raises:
        HTTPException: If the user is not found or the user tries to update themselves.
        HTTPException: If there is an error updating the user.
    """
    user = user_crud.get_one(db, User.id == user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found. Cannot update.",
        )
    try:
        user = user_crud.update(db, user, user_update)
    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update user with id {user_id}. Error: {str(e)}",
        ) from e  # pragma: no cover
    return user
