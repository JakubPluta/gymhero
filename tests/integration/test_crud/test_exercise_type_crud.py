import pytest
from sqlalchemy.exc import IntegrityError

from gymhero.crud import exercise_type_crud
from gymhero.models import ExerciseType
from gymhero.schemas.exercise_type import ExerciseTypeCreate


def test_can_fetch_all_exercise_type(seed_exercise_types, get_test_db):
    """Test that we can fetch all ExerciseTypes"""
    exercise_types = exercise_type_crud.get_many(get_test_db)
    print(exercise_types)
    assert len(exercise_types) > 0


def test_can_fetch_exercise_type_by_id(seed_exercise_types, get_test_db):
    """Test that we can fetch a ExerciseType by id"""
    exercise_type = exercise_type_crud.get_one(get_test_db, ExerciseType.id == 1)
    assert exercise_type.id == 1 and isinstance(exercise_type, ExerciseType)


def test_should_not_fetch_exercise_type_that_not_exists(
    seed_exercise_types, get_test_db
):
    """Test that we can fetch a ExerciseType if it doesn't exist"""
    exercise_type = exercise_type_crud.get_one(get_test_db, ExerciseType.id == 4324321)
    assert exercise_type is None
    exercise_type = exercise_type_crud.get_one(get_test_db, ExerciseType.name == "cool")
    assert exercise_type is None


def test_can_fetch_exercise_type_by_name(seed_exercise_types, get_test_db):
    """Test that we can fetch a ExerciseType by name"""
    exercise_type = exercise_type_crud.get_one(
        get_test_db, ExerciseType.name == "Strength"
    )
    assert exercise_type.name == "Strength" and isinstance(exercise_type, ExerciseType)


def test_can_delete_exercise_type_by_id(seed_exercise_types, get_test_db):
    """Test that we can delete a ExerciseType by id"""
    exercise_type_to_delete = exercise_type_crud.get_one(
        get_test_db, ExerciseType.id == 1
    )
    exercise_type_crud.delete(get_test_db, exercise_type_to_delete)
    exercise_type = exercise_type_crud.get_one(get_test_db, ExerciseType.id == 1)
    assert exercise_type is None


def test_should_rise_exception_when_delete_exercise_type_that_not_exists(get_test_db):
    """Test that we can delete a ExerciseType if it doesn't exist"""
    exercise_type = exercise_type_crud.get_one(get_test_db, ExerciseType.id == 1)
    with pytest.raises(Exception):
        exercise_type_crud.delete(get_test_db, exercise_type)


def can_update_exercise_type(seed_exercise_types, get_test_db):
    """Test that we can update a ExerciseType by id"""
    exercise_type_to_update = exercise_type_crud.get_one(
        get_test_db, ExerciseType.id == 1
    )
    exercise_type_to_update.name = "abc"
    exercise_type_crud.update(get_test_db, exercise_type_to_update)
    exercise_type = exercise_type_crud.get_one(get_test_db, ExerciseType.id == 1)
    assert exercise_type.name == "abc"


def test_should_rise_exception_when_update_exercise_type_that_not_exists(get_test_db):
    """Test that we can update a ExerciseType if it doesn't exist"""
    exercise_type = exercise_type_crud.get_one(get_test_db, ExerciseType.id == 1)
    with pytest.raises(Exception):
        exercise_type_crud.update(get_test_db, exercise_type)


def test_can_create_exercise_type(get_test_db):
    """Test that we can create a ExerciseType"""
    obj_in = ExerciseTypeCreate(name="test")

    assert (
        exercise_type_crud.get_one(get_test_db, ExerciseType.name == obj_in.name)
        is None
    )

    exercise = exercise_type_crud.create(get_test_db, obj_in)
    fetched_exercise = exercise_type_crud.get_one(
        get_test_db, ExerciseType.id == exercise.id
    )

    assert (
        exercise and isinstance(exercise, ExerciseType) and fetched_exercise == exercise
    )


def test_should_not_create_exercise_type_if_already_exists(get_test_db):
    """Test that we can create a ExerciseType if it already exists"""
    obj_in = ExerciseTypeCreate(name="test")
    exercise_type = exercise_type_crud.create(get_test_db, obj_in)
    assert exercise_type and isinstance(exercise_type, ExerciseType)
    with pytest.raises(IntegrityError) as e:
        exercise_type_crud.create(get_test_db, obj_in)

    assert "duplicate key value violates unique constraint" in str(e.value)
