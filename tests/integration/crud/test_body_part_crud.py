import pytest
from sqlalchemy.exc import IntegrityError

from gymhero.crud import bodypart_crud
from gymhero.models.body_part import BodyPart
from gymhero.schemas.body_part import BodyPartCreate


def test_can_fetch_all_body_parts(seed_body_parts, get_test_db):
    """Test that we can fetch all body_parts"""
    body_parts = bodypart_crud.get_many(get_test_db)
    assert len(body_parts) > 0


def test_can_fetch_body_part_by_id(seed_body_parts, get_test_db):
    """Test that we can fetch a body_part by id"""
    body_part = bodypart_crud.get_one(get_test_db, BodyPart.id == 1)
    assert body_part.id == 1 and isinstance(body_part, BodyPart)


def test_should_not_fetch_body_part_that_not_exists(get_test_db):
    body_part = bodypart_crud.get_one(get_test_db, BodyPart.id == 1)
    assert body_part is None


def test_can_fetch_body_part_by_name(seed_body_parts, get_test_db):
    """Test that we can fetch a body_part by name"""
    body_part = bodypart_crud.get_one(get_test_db, BodyPart.name == "Biceps")
    assert body_part.name == "Biceps" and isinstance(body_part, BodyPart)


def test_can_delete_body_part_by_id(seed_body_parts, get_test_db):
    """Test that we can delete a body_part by id"""
    body_part_to_delete = bodypart_crud.get_one(get_test_db, BodyPart.id == 1)
    bodypart_crud.delete(get_test_db, body_part_to_delete)
    body_part = bodypart_crud.get_one(get_test_db, BodyPart.id == 1)
    assert body_part is None


def test_should_rise_exception_when_delete_body_part_that_not_exists(get_test_db):
    """Test that we can delete a body_part if it doesn't exist"""
    body_part = bodypart_crud.get_one(get_test_db, BodyPart.id == 1)
    with pytest.raises(Exception):
        bodypart_crud.delete(get_test_db, body_part)


def can_update_body_part(seed_body_parts, get_test_db):
    """Test that we can update a body_part by id"""
    body_part_to_update = bodypart_crud.get_one(get_test_db, BodyPart.id == 1)
    body_part_to_update.name = "abc"
    bodypart_crud.update(get_test_db, body_part_to_update)
    body_part = bodypart_crud.get_one(get_test_db, BodyPart.id == 1)
    assert body_part.name == "abc"


def test_should_rise_exception_when_update_body_part_that_not_exists(get_test_db):
    """Test that we can update a body_part if it doesn't exist"""
    body_part = bodypart_crud.get_one(get_test_db, BodyPart.id == 1)
    with pytest.raises(Exception):
        bodypart_crud.update(get_test_db, body_part)


def test_can_create_body_part(get_test_db):
    """Test that we can create a body_part"""
    obj_in = BodyPartCreate(name="test")

    assert bodypart_crud.get_one(get_test_db, BodyPart.name == obj_in.name) is None

    body_part = bodypart_crud.create(get_test_db, obj_in)
    fetched_body_part = bodypart_crud.get_one(get_test_db, BodyPart.id == body_part.id)

    assert body_part and isinstance(body_part, BodyPart)
    assert fetched_body_part == body_part


def test_should_not_create_body_part_if_already_exists(get_test_db):
    """Test that we can create a body_part if it already exists"""
    obj_in = BodyPartCreate(name="test")
    body_part = bodypart_crud.create(get_test_db, obj_in)
    assert body_part and isinstance(body_part, BodyPart)
    with pytest.raises(IntegrityError) as e:
        bodypart_crud.create(get_test_db, obj_in)

    assert "duplicate key value violates unique constraint" in str(e.value)
