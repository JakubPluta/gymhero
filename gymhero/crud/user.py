from typing import Optional

from sqlalchemy.orm import Session

from gymhero.crud.base import CRUDRepository
from gymhero.models.user import User
from gymhero.security import verify_password


class UserCRUDRepository(CRUDRepository):
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get a user by email.

        Parameters:
            db (Session): The database session.
            email (str): The email of the user.

        Returns:
            Optional[User]: The user found by email, or None if not found.
        """
        return self.get_one(db, self._model.email == email)

    @staticmethod
    def is_super_user(user: User) -> bool:
        """
        Check if the given user is a super user.

        Parameters:
            user (User): The user to check.

        Returns:
            bool: True if the user is a super user, False otherwise.
        """
        return user.is_superuser

    @staticmethod
    def is_active_user(user: User) -> bool:
        """
        Check if a user is active.

        Parameters:
            user (User): The user object to check.

        Returns:
            bool: True if the user is active, False otherwise.
        """
        return user.is_active

    @staticmethod
    def deactivate_user(db: Session, user: User) -> User:
        """Deactivates a user by setting their `is_active` flag to `False`.

        Parameters:
            db (Session): The database session object.
            user (User): The user to deactivate.

        Returns:
            User: The deactivated user object.
        """
        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticates a user with the given email and password.

        Parameters:
            db (Session): The database session object.
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            Optional[User]: The authenticated user if successful, None otherwise.
        """
        user = self.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user_crud = UserCRUDRepository(model=User)
