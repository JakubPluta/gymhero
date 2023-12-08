from sqlalchemy import CursorResult, text

from scripts.core._initdb import seed_database
from scripts.core._initsu import seed_superuser


def test_can_seed_database(get_test_db) -> None:
    """Test that we can connect to the database"""
    seed_database("test")
    session = get_test_db
    record: CursorResult = session.execute(text("SELECT * FROM exercises")).fetchone()

    for table in ["exercises", "exercise_types", "levels", "body_parts", "users"]:
        record = session.execute(text(f"SELECT * FROM {table}")).fetchone()
        assert record and len(record) > 0


def test_can_create_superuser(get_test_db, test_settings) -> None:
    """Test that we can create a superuser"""
    seed_superuser("test")

    session = get_test_db
    record = session.execute(text("SELECT * FROM users")).fetchone()
    assert record.id == 1
    assert record.full_name == test_settings.FIRST_SUPERUSER_USERNAME
    assert record.email == test_settings.FIRST_SUPERUSER_EMAIL
