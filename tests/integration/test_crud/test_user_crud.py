import pytest
from sqlalchemy.exc import IntegrityError
from gymhero.crud import user_crud
from gymhero.models.user import User
from gymhero.schemas.user import UserCreate, UserInDB, UserUpdate
from gymhero.security import get_password_hash
from scripts.core._initsu import seed_superuser


@pytest.fixture(autouse=True)
def seed_test_superuser():
    return seed_superuser("test")


def test_can_get_user_by_email(get_test_db):
    """Test that we can fetch a user by email"""
    user = user_crud.get_user_by_email(get_test_db, "testuser@mail.com")
    assert user.email == "testuser@mail.com" and isinstance(user, User)


def test_can_get_user_by_id(get_test_db):
    """Test that we can fetch a user by id"""
    user = user_crud.get_one(get_test_db, User.id == 1)
    assert user.id == 1 and isinstance(user, User)


def test_can_deactivate_user(get_test_db):
    """Test that we can fetch a user by name"""
    user = user_crud.get_one(get_test_db, User.id == 1)

    assert user.is_active is True
    user_crud.deactivate_user(get_test_db, user)
    user = user_crud.get_one(get_test_db, User.id == 1)
    assert user.is_active is False


def test_can_authenticate_user(get_test_db):
    """Test that we can fetch a user by name"""
    user = user_crud.authenticate_user(get_test_db, "testuser@mail.com", "password")
    assert user is not None


def test_should_not_authenticate_user_if_password_incorrect(get_test_db):
    """Test that we can fetch a user by name"""
    user = user_crud.authenticate_user(
        get_test_db, "testuser@mail.com", "wrong_password"
    )
    assert user is None


def test_can_create_user(get_test_db):
    """Test that we can create a user"""
    user_create = UserCreate(email="newuser@mail.com", password="password")
    user_in = UserInDB(
        **user_create.model_dump(),
        hashed_password=get_password_hash(user_create.password),
    )
    user = user_crud.create(get_test_db, user_in)
    assert (
        user
        and isinstance(user, User)
        and user.email == "newuser@mail.com"
        and user.is_active is True
        and user.is_superuser is False
        and user.hashed_password != user_create.password
    )


def test_should_not_create_user_if_email_in_use(get_test_db):
    """Test that we can create a user"""
    user = user_crud.get_user_by_email(get_test_db, "testuser@mail.com")
    assert user is not None

    user_create = UserCreate(email="testuser@mail.com", password="password")
    user_in = UserInDB(
        **user_create.model_dump(),
        hashed_password=get_password_hash(user_create.password),
    )
    with pytest.raises(IntegrityError):
        user_crud.create(get_test_db, user_in)


def test_should_update_user(get_test_db):
    """Test that we can update a user"""
    user = user_crud.get_one(get_test_db, User.id == 1)
    name_before = user.full_name
    user_update = UserUpdate(full_name="Test Test")
    user = user_crud.update(get_test_db, user, user_update)
    assert user.full_name == "Test Test"
    assert user.full_name != name_before


def test_should_delete_user(get_test_db):
    """Test that we can delete a user"""
    user = user_crud.get_one(get_test_db, User.id == 1)
    user_crud.delete(get_test_db, user)
    user = user_crud.get_one(get_test_db, User.id == 1)
    assert user is None


def test_should_properly_check_user_status_and_role(get_test_db):
    """Test that we can check user's status and role"""
    user = user_crud.get_one(get_test_db, User.id == 1)
    assert user.is_active is True
    assert user.is_superuser is True


def test_should_properly_check_user_role(get_test_db):
    """Test that we can check user's role"""
    user = user_crud.get_one(get_test_db, User.id == 1)
    assert user.is_superuser is True
