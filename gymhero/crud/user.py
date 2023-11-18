from typing import Optional

from gymhero.models.user import User
from gymhero.crud.base import CRUDRepository


class UserCRUDRepository(CRUDRepository):
    def get_user_by_email(self, db, email) -> Optional[User]:
        return self.get_one_record(db, self._model.email == email)

    @staticmethod
    def is_super_user(user: User) -> bool:
        return user.is_superuser

    @staticmethod
    def is_active_user(user: User) -> bool:
        return user.is_active


user_crud = UserCRUDRepository(model=User)
