from typing import Optional

from sqlalchemy.orm import Session

from gymhero.models.user import User
from gymhero.crud.base import CRUDRepository


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


user_crud = UserCRUDRepository(model=User)
