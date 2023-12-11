from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from gymhero.crud.training_plan import training_plan_crud
from gymhero.models.training_plan import TrainingPlan
from gymhero.models.training_unit import TrainingUnit
from gymhero.schemas.training_plan import TrainingPlanCreate, TrainingPlanUpdate

from gymhero.crud import exercise_crud
from scripts.core.utils import _create_first_user


@pytest.fixture
def db():
    return MagicMock(spec=Session)


@pytest.fixture
def _training_unit(get_test_db, seed_test_database):
    tu = TrainingUnit(id=1, name="test", description="test")
    exercises = exercise_crud.get_many(get_test_db, skip=0, limit=10)
    tu.exercises.extend(exercises)
    return tu


def test_add_new_training_unit_to_plan(get_test_db, _training_unit):
    # Arrange
    training_plan = TrainingPlan(id=1, name="test", description="test")

    # Act
    result = training_plan_crud.add_training_unit_to_training_plan(
        get_test_db, training_plan, _training_unit
    )

    # Assert
    assert result is not None and len(result.training_units) == 1
    assert result.training_units[0].exercises == _training_unit.exercises


def test_cant_add_new_training_unit_if_already_exists(get_test_db, _training_unit):
    # Arrange
    training_plan = TrainingPlan(id=1, name="test", description="test")

    # Act
    training_plan_crud.add_training_unit_to_training_plan(
        get_test_db, training_plan, _training_unit
    )
    training_plan_crud.add_training_unit_to_training_plan(
        get_test_db, training_plan, _training_unit
    )

    # Assert
    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert len(training_plan.training_units) == 1


def test_can_create_training_plan(get_test_db):
    # Arrange
    training_plan_crud.create(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
    )

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.name == "test")
    assert training_plan is not None and training_plan.name == "test"


def test_cannot_create_training_plan_with_existing_name(get_test_db):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    # Arrange
    training_plan_crud.create_with_owner(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
        owner_id=1,
    )

    # Act
    with pytest.raises(IntegrityError) as e:
        training_plan_crud.create_with_owner(
            get_test_db,
            TrainingPlanCreate(
                name="test",
                description="test",
            ),
            owner_id=1,
        )
    assert "duplicate key value violates unique constraint" in str(e.value)


def test_can_get_many_training_plans(get_test_db):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    for i in range(10):
        training_plan_crud.create_with_owner(
            get_test_db,
            TrainingPlanCreate(
                name=f"test_{i}",
                description="test",
            ),
            owner_id=1,
        )

    training_plans = training_plan_crud.get_many(get_test_db, skip=0, limit=10)
    assert len(training_plans) == 10


def test_can_get_one_training_plan(get_test_db):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    training_plan_crud.create_with_owner(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
        owner_id=1,
    )

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.name == "test")
    assert training_plan is not None and training_plan.name == "test"

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert training_plan is not None and training_plan.id == 1


def test_can_get_mine_training_plans(get_test_db):
    u1 = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    u2 = _create_first_user(
        get_test_db, "abc@testing.com", "abcdefg", "abcdefg", False, True
    )
    training_plan_crud.create_with_owner(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
        owner_id=1,
    )
    training_plan_crud.create_with_owner(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
        owner_id=2,
    )

    training_plans = training_plan_crud.get_many_for_owner(get_test_db, owner_id=2)
    assert len(training_plans) == 1


def test_can_update_training_plan(get_test_db):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    training_plan_crud.create_with_owner(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
        owner_id=1,
    )

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert training_plan is not None and training_plan.name == "test"

    training_plan_crud.update(
        get_test_db,
        training_plan,
        TrainingPlanUpdate(
            name="test_updated",
            description="test_updated",
        ),
    )

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert training_plan is not None and training_plan.name == "test_updated"


def test_can_delete_training_plan(get_test_db):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    training_plan_crud.create_with_owner(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
        owner_id=1,
    )

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert training_plan is not None and training_plan.name == "test"

    training_plan_crud.delete(get_test_db, training_plan)

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert training_plan is None


def test_can_get_training_units_in_training_plan(get_test_db):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    training_plan_crud.create_with_owner(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
        owner_id=1,
    )

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert training_plan is not None and training_plan.name == "test"

    training_plan_crud.add_training_unit_to_training_plan(
        get_test_db,
        training_plan,
        TrainingUnit(name="test", description="test", owner_id=1),
    )
    training_units = training_plan_crud.get_training_units_in_training_plan(
        training_plan
    )
    assert len(training_units) == 1


def test_can_remove_training_unit_from_training_plan(get_test_db):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    training_plan_crud.create_with_owner(
        get_test_db,
        TrainingPlanCreate(
            name="test",
            description="test",
        ),
        owner_id=1,
    )

    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert training_plan is not None and training_plan.name == "test"

    training_unit = TrainingUnit(name="test", description="test", owner_id=1)
    training_plan_crud.add_training_unit_to_training_plan(
        get_test_db, training_plan, training_unit
    )

    training_plan_crud.remove_training_unit_from_training_plan(
        get_test_db, training_plan, training_unit
    )
    training_plan = training_plan_crud.get_one(get_test_db, TrainingPlan.id == 1)
    assert training_plan is not None and training_plan.training_units == []
