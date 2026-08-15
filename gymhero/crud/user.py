from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud.base import CRUDRepository
from gymhero.models.user import User
from gymhero.security import verify_password


class UserCRUDRepository(CRUDRepository[User]):
    async def get_user_by_email(self, db: AsyncSession, email: str) -> User | None:
        return await self.get_one(db, self._model.email == email)

    @staticmethod
    def is_super_user(user: User) -> bool:
        return bool(user.is_superuser)

    @staticmethod
    def is_active_user(user: User) -> bool:
        return bool(user.is_active)

    @staticmethod
    async def deactivate_user(db: AsyncSession, user: User) -> User:
        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate_user(
        self, db: AsyncSession, email: str, password: str
    ) -> User | None:
        user = await self.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user_crud = UserCRUDRepository(model=User)
