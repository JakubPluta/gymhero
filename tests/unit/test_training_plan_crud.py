import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from gymhero.crud.training_plan import training_plan_crud
from gymhero.models.training_unit import TrainingUnit
from gymhero.models.training_plan import TrainingPlan


@pytest.fixture
def db():
    return MagicMock(spec=Session)


def test_add_new_training_unit(db):
    # Arrange
    training_plan = TrainingPlan(id=1, name="test", description="test")
    training_unit = TrainingUnit(id=1, name="test", description="test")

    # Act
    result = training_plan_crud.add_training_unit_to_training_plan(
        db, training_plan, training_unit
    )

    # Assert
    print(result)
    assert result is not None
    assert len(training_plan.training_units) == 1
    assert training_plan.training_units[0] == training_unit


def test_add_existing_training_unit(db):
    # Arrange
    training_plan = TrainingPlan()
    training_unit = TrainingUnit()
    training_plan.training_units.append(training_unit)

    # Act
    result = training_plan_crud.add_training_unit_to_training_plan(
        db, training_plan, training_unit
    )

    # Assert
    assert result is None
    assert len(training_plan.training_units) == 1
