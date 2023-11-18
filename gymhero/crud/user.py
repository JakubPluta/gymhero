from typing import Optional, List, Type

from gymhero.models import User
from gymhero.models.user import User
from sqlalchemy.orm import Session
from gymhero.schemas.user import UserCreate, UserUpdate, UserInDB, UserBase
from logging import getLogger


log = getLogger(__name__)


def get_all_users(db: Session) -> list[Type[User]]:
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def check_if_users_is_active(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id, User.is_active is True).first()


def check_if_user_is_superuser(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id, User.is_superuser is True).first()


def create_user(db: Session, user: UserInDB) -> User:
    log.info("creating user")
    user_orm: User = User(**user.model_dump())
    db.add(user_orm)
    db.commit()
    db.refresh(user_orm)
    return user_orm
