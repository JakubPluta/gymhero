from typing import Optional

from sqlalchemy.orm import Session

from gymhero.models.user import User
from gymhero.crud.base import CRUDRepository
from gymhero.security import verify_password


class UserCRUDRepository(CRUDRepository):
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return self.get_one_record(db, self._model.email == email)

    @staticmethod
    def is_super_user(user: User) -> bool:
        return user.is_superuser

    @staticmethod
    def is_active_user(user: User) -> bool:
        return user.is_active

    @staticmethod
    def deactivate_user(db: Session, user: User) -> User:
        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        user = self.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user_crud = UserCRUDRepository(model=User)
