import pytest
from sqlalchemy.exc import IntegrityError

from gymhero.crud import level_crud
from gymhero.models.level import Level
from gymhero.schemas.level import LevelCreate


def test_can_fetch_all_levels(seed_levels, get_test_db):
    """Test that we can fetch all levels"""
    levels = level_crud.get_many(get_test_db)
    assert len(levels) > 0


def test_can_fetch_level_by_id(seed_levels, get_test_db):
    """Test that we can fetch a level by id"""
    level = level_crud.get_one(get_test_db, Level.id == 1)
    assert level.id == 1 and isinstance(level, Level)


def test_should_not_fetch_level_that_not_exists(get_test_db):
    level = level_crud.get_one(get_test_db, Level.id == 1)
    assert level is None


def test_can_fetch_level_by_name(seed_levels, get_test_db):
    """Test that we can fetch a level by name"""
    level = level_crud.get_one(get_test_db, Level.name == "Beginner")
    assert level.name == "Beginner" and isinstance(level, Level)


def test_can_delete_level_by_id(seed_levels, get_test_db):
    """Test that we can delete a level by id"""
    level_to_delete = level_crud.get_one(get_test_db, Level.id == 1)
    level_crud.delete(get_test_db, level_to_delete)
    level = level_crud.get_one(get_test_db, Level.id == 1)
    assert level is None


def test_should_rise_exception_when_delete_level_that_not_exists(get_test_db):
    """Test that we can delete a level if it doesn't exist"""
    level = level_crud.get_one(get_test_db, Level.id == 1)
    with pytest.raises(Exception):
        level_crud.delete(get_test_db, level)


def can_update_level(seed_levels, get_test_db):
    """Test that we can update a level by id"""
    level_to_update = level_crud.get_one(get_test_db, Level.id == 1)
    level_to_update.name = "abc"
    level_crud.update(get_test_db, level_to_update)
    level = level_crud.get_one(get_test_db, Level.id == 1)
    assert level.name == "abc"


def test_should_rise_exception_when_update_level_that_not_exists(get_test_db):
    """Test that we can update a level if it doesn't exist"""
    level = level_crud.get_one(get_test_db, Level.id == 1)
    with pytest.raises(Exception):
        level_crud.update(get_test_db, level)


def test_can_create_level(get_test_db):
    """Test that we can create a level"""
    obj_in = LevelCreate(name="test")

    assert level_crud.get_one(get_test_db, Level.name == obj_in.name) is None

    level = level_crud.create(get_test_db, obj_in)
    fetched_level = level_crud.get_one(get_test_db, Level.id == level.id)

    assert level and isinstance(level, Level)
    assert fetched_level == level


def test_should_not_create_level_if_already_exists(get_test_db):
    """Test that we can create a level if it already exists"""
    obj_in = LevelCreate(name="test")
    level = level_crud.create(get_test_db, obj_in)
    assert level and isinstance(level, Level)
    with pytest.raises(IntegrityError) as e:
        level_crud.create(get_test_db, obj_in)

    assert "duplicate key value violates unique constraint" in str(e.value)
