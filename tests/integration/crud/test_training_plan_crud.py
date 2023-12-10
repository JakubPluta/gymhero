from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from gymhero.crud.training_plan import training_plan_crud
from gymhero.models.training_plan import TrainingPlan
from gymhero.models.training_unit import TrainingUnit

from gymhero.crud import exercise_crud


@pytest.fixture
def db():
    return MagicMock(spec=Session)


@pytest.fixture
def _training_unit(get_test_db, seed_test_database):
    tu = TrainingUnit(id=1, name="test", description="test")
    exercises = exercise_crud.get_many(get_test_db, skip=0, limit=10)
    tu.exercises.extend(exercises)
    return tu


def test_add_new_training_unit(get_test_db, _training_unit):
    # Arrange
    training_plan = TrainingPlan(id=1, name="test", description="test")

    # Act
    result = training_plan_crud.add_training_unit_to_training_plan(
        get_test_db, training_plan, _training_unit
    )

    # Assert
    assert result is not None and len(result.training_units) == 1
    assert result.training_units[0].exercises == _training_unit.exercises


def test_add_new_training_unit(get_test_db, _training_unit):
    # Arrange
    training_plan = TrainingPlan(id=1, name="test", description="test")

    # Act
    result = training_plan_crud.add_training_unit_to_training_plan(
        get_test_db, training_plan, _training_unit
    )

    result = training_plan_crud.add_training_unit_to_training_plan(
        get_test_db, training_plan, _training_unit
    )

    # Assert
    assert result is not None and len(result.training_units) == 1
    assert result.training_units[0].exercises == _training_unit.exercises
