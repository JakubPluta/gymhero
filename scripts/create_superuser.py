"""Create first user"""

from sqlalchemy.orm import Session
from gymhero.database.db import get_ctx_db
from gymhero.log import get_logger
from gymhero.security import get_password_hash
from gymhero.config import settings
from gymhero.crud.user import user_crud
from gymhero.schemas.user import UserInDB

log = get_logger(__name__, level="DEBUG")


def create_first_superuser(db: Session):
    """Create first superuser"""
    user = user_crud.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)

    if not user:
        user_in = UserInDB(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            full_name=settings.FIRST_SUPERUSER_USERNAME,
        )
        user_crud.create(db, obj_create=user_in)
        log.info("Created first superuser: %s", user)
    else:
        log.info("First superuser already exists: %s", user)


if __name__ == "__main__":
    log.info("Creating first superuser")
    with get_ctx_db() as database:
        create_first_superuser(database)
