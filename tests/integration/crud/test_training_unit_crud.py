import pytest
from gymhero.crud import exercise_crud, training_unit_crud
from gymhero.models import Exercise, TrainingUnit
from gymhero.schemas.training_unit import (
    TrainingUnitCreate,
    TrainingUnitInDB,
    TrainingUnitUpdate,
)
from tests.conftest import override_get_db


@pytest.fixture(autouse=True, scope="function")
def seed_training_units(get_test_db):
    training_units = [
        TrainingUnitCreate(name="test1", description="test1"),
        TrainingUnitCreate(name="test2", description="test2"),
        TrainingUnitCreate(name="test3", description="test3"),
    ]

    for training_unit in training_units:
        training_unit_crud.create(get_test_db, training_unit)


def test_can_fetch_all_training_units(get_test_db):
    """Test that we can fetch all training_units"""
    training_units = training_unit_crud.get_many(get_test_db)
    assert len(training_units) > 0


def test_can_fetch_training_unit_by_id(get_test_db):
    """Test that we can fetch a training_unit by id"""
    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)
    assert training_unit.id == 1 and isinstance(training_unit, TrainingUnit)


def test_can_fetch_training_unit_by_name(get_test_db):
    """Test that we can fetch a training_unit by name"""
    training_unit = training_unit_crud.get_one(
        get_test_db, TrainingUnit.name == "test1"
    )
    assert training_unit.name == "test1" and isinstance(training_unit, TrainingUnit)


def test_can_delete_training_unit_by_id(get_test_db):
    """Test that we can delete a training_unit by id"""
    training_unit_to_delete = training_unit_crud.get_one(
        get_test_db, TrainingUnit.id == 1
    )
    training_unit_crud.delete(get_test_db, training_unit_to_delete)
    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)
    assert training_unit is None


def test_can_update_training_unit_by_id(get_test_db):
    """Test that we can update a training_unit by id"""
    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)
    training_unit_to_update = TrainingUnitUpdate(name="abc")
    training_unit_crud.update(get_test_db, training_unit, training_unit_to_update)
    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)
    assert training_unit.name == "abc"


def test_can_add_exercise_to_training_unit(get_test_db, seed_test_database):
    """Test that we can add an exercise to a training_unit"""
    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)
    exercise_before = training_unit_crud.get_exercises_in_training_unit(training_unit)
    assert len(exercise_before) == 0

    exercise = exercise_crud.get_one(get_test_db, Exercise.id == 1)
    training_unit = training_unit_crud.add_exercise_to_training_unit(
        get_test_db, training_unit, exercise
    )
    exercise_after = training_unit_crud.get_exercises_in_training_unit(training_unit)
    assert len(exercise_after) == 1 and exercise_after[0].id == exercise.id


def test_cant_add_exercise_to_training_unit_if_already_in(
    get_test_db, seed_test_database
):
    """Test that we can't add an exercise to a training_unit if it doesn't exist"""
    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)

    exercise = exercise_crud.get_one(get_test_db, Exercise.id == 1)
    training_unit = training_unit_crud.add_exercise_to_training_unit(
        get_test_db, training_unit, exercise
    )
    assert len(training_unit.exercises) == 1

    training_unit_crud.add_exercise_to_training_unit(
        get_test_db, training_unit, exercise
    )

    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)
    assert len(training_unit.exercises) == 1


def test_can_remove_exercise_from_training_unit(get_test_db, seed_test_database):
    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)
    exercise = exercise_crud.get_one(get_test_db, Exercise.id == 1)
    training_unit = training_unit_crud.add_exercise_to_training_unit(
        get_test_db, training_unit, exercise
    )

    training_unit = training_unit_crud.remove_exercise_from_training_unit(
        get_test_db, training_unit, exercise
    )
    assert len(training_unit.exercises) == 0

    with pytest.raises(ValueError) as exc:
        training_unit = training_unit_crud.remove_exercise_from_training_unit(
            get_test_db, training_unit, exercise
        )

    assert str(exc.value) == "Exercise not found in training unit"


def test_should_check_if_exercise_in_training_unit(get_test_db):
    training_unit = training_unit_crud.get_one(get_test_db, TrainingUnit.id == 1)
    exercise = exercise_crud.get_one(get_test_db, Exercise.id == 1)
    assert (
        training_unit_crud.check_if_exercise_in_training_unit(training_unit, exercise)
        is False
    )
