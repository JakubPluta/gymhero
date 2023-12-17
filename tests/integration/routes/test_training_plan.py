import pytest
from gymhero.crud.training_unit import training_unit_crud
from gymhero.crud.training_plan import training_plan_crud

from gymhero.models.training_plan import TrainingPlan
from gymhero.schemas.training_plan import TrainingPlanCreate
from gymhero.security import create_access_token
from scripts.core.utils import _create_first_user


@pytest.fixture(autouse=True, scope="function")
def seed_training_plans(get_test_db):
    u = _create_first_user(get_test_db, "admin@admin.com", "admin", "Admin", True, True)

    training_plans = [
        TrainingPlanCreate(name=f"test_{i}", description=f"test_{i}") for i in range(5)
    ]

    for tp in training_plans:
        training_plan_crud.create_with_owner(get_test_db, tp, u.id)

    u2 = _create_first_user(get_test_db, "abc@abc.com", "abc", "abc", False, True)
    training_plans = [
        TrainingPlanCreate(name=f"test_{i}", description=f"test_{i}")
        for i in range(6, 9)
    ]

    for tp in training_plans:
        training_plan_crud.create_with_owner(get_test_db, tp, u2.id)


def test_can_get_all_training_plans(test_client, valid_jwt_token, get_test_db):
    response = test_client.get(
        "/training-plans/all?skip=0&limit=3",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and len(response.json()) == 3

    response = test_client.get(
        "/training-plans/all?skip=-10&limit=-5",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 422

    response = test_client.get(
        "/training-plans/all?skip=10&limit=1",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and len(response.json()) == 0

    response = test_client.get("/training-plans/all?skip=0&limit=10000")
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )

    jwt_token_2 = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-plans/all?skip=0&limit=3",
        headers={"Authorization": jwt_token_2},
    )
    assert response.status_code == 403


def test_can_get_all_training_plans_for_owner(
    test_client, valid_jwt_token, get_test_db
):
    response = test_client.get(
        "/training-plans/all/my?skip=0&limit=3",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and len(response.json()) == 3

    jwt_token_2 = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-plans/all/my?skip=0&limit=1",
        headers={"Authorization": jwt_token_2},
    )
    assert response.status_code == 200 and len(response.json()) == 1

    response = test_client.get(
        "/training-plans/all/my?skip=0&limit=1",
    )
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )


def test_can_get_one_training_plan(test_client, get_test_db, valid_jwt_token):
    response = test_client.get(
        "/training-plans/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200 and response.json()["id"] == 1

    response = test_client.get(
        "/training-plans/10", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    # Test with JWT of another user
    jwt_token_2 = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-plans/1", headers={"Authorization": jwt_token_2}
    )
    assert response.status_code == 404
    response = test_client.get(
        "/training-plans/6", headers={"Authorization": jwt_token_2}
    )
    assert response.status_code == 200

    response = test_client.get(
        "/training-plans/6", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200
