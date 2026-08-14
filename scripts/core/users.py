from sqlalchemy.orm import Session

from gymhero.config import Settings
from gymhero.log import get_logger
from gymhero.models.user import User
from gymhero.security import get_password_hash

log = get_logger(__name__)


def get_or_create_user(
    db: Session,
    email: str,
    password: str,
    full_name: str | None = None,
    is_superuser: bool = True,
    is_active: bool = True,
) -> User:
    # Sync ORM on purpose: seeding is offline tooling; the CRUD repos are async.
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        is_superuser=is_superuser,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log.debug("Created user %s", email)
    return user


def create_first_superuser(db: Session, settings: Settings) -> User:
    """Create the configured first superuser (from ``settings``) if absent."""
    return get_or_create_user(
        db,
        email=settings.FIRST_SUPERUSER_EMAIL,
        password=settings.FIRST_SUPERUSER_PASSWORD.get_secret_value(),
        full_name=settings.FIRST_SUPERUSER_USERNAME,
        is_superuser=True,
    )
