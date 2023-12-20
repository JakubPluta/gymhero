import pytest

from gymhero.crud.training_plan import training_plan_crud
from gymhero.crud.training_unit import training_unit_crud
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


def test_can_get_all_training_plans(test_client, valid_jwt_token):
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


def test_can_get_all_training_plans_for_owner(test_client, valid_jwt_token):
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


def test_can_get_one_training_plan(test_client, valid_jwt_token):
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


def test_can_get_one_training_plan_by_name(test_client, valid_jwt_token):
    response = test_client.get(
        "/training-plans/name/test_0", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200 and response.json()["name"] == "test_0"

    response = test_client.get(
        "/training-plans/name/test200", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    response = test_client.get(
        "/training-plans/name/test_6", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    jwt_token_2 = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-plans/name/test_0", headers={"Authorization": jwt_token_2}
    )
    assert response.status_code == 404

    response = test_client.get(
        "/training-plans/name/test_0",
    )
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )


def can_get_training_plans_by_name_for_super_user(
    test_client,
    valid_jwt_token,
):
    response = test_client.get(
        "/training-plans/name/test_0/superuser",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200

    response = test_client.get("/training-plans/name/test_0/superuser")
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )

    jwt_token_2 = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-plans/name/test_0/superuser", headers={"Authorization": jwt_token_2}
    )
    assert response.status_code == 403

    response = test_client.get(
        "/training-plans/name/test_12345/superuser",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 404
        and response.json()["detail"] == "Training plans with name test_12345 not found"
    )


def test_can_create_training_plan(test_client, valid_jwt_token):
    response = test_client.post(
        "/training-plans",
        json={"name": "test_0", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 409

    jwt_token_2 = "Bearer " + create_access_token(2)
    response = test_client.post(
        "/training-plans",
        json={"name": "test_0", "description": "test"},
    )
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )
    response = test_client.post(
        "/training-plans",
        headers={"Authorization": jwt_token_2},
        json={"name": "test_0", "description": "test"},
    )
    assert response.status_code == 201


def test_can_delete_training_plan(test_client, valid_jwt_token):
    response = test_client.delete(
        "/training-plans/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200

    response = test_client.delete(
        "/training-plans/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    response = test_client.delete(
        "/training-plans/432431", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    response = test_client.delete(
        "/training-plans/432431", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    jwt_two = "Bearer " + create_access_token(2)
    response = test_client.delete(
        "/training-plans/2", headers={"Authorization": jwt_two}
    )
    assert response.status_code == 403

    response = test_client.delete(
        "/training-plans/6", headers={"Authorization": jwt_two}
    )
    assert response.status_code == 200


def test_can_update_training_plan(test_client, valid_jwt_token):
    response = test_client.put(
        "/training-plans/1",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test", "description": "test"},
    )
    assert response.status_code == 200 and response.json()["name"] == "test"

    response = test_client.put(
        "/training-plans/134343",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test", "description": "test"},
    )
    assert response.status_code == 404

    jwt_two = "Bearer " + create_access_token(2)
    response = test_client.put(
        "/training-plans/1",
        headers={"Authorization": jwt_two},
        json={"name": "test1", "description": "test"},
    )
    assert response.status_code == 403

    response = test_client.put(
        "/training-plans/6",
        headers={"Authorization": jwt_two},
        json={"name": "test1", "description": "test"},
    )
    assert response.status_code == 200


def test_can_get_plans_for_super_user(
    test_client,
    valid_jwt_token,
):
    response = test_client.get(
        "/training-plans/name/test_6/superuser",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 200
        and isinstance(response.json(), list)
        and len(response.json()) == 1
    )

    response = test_client.get(
        "/training-plans/name/test_1/superuser",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 200
        and isinstance(response.json(), list)
        and len(response.json()) == 1
    )

    response = test_client.get(
        "/training-plans/name/test_555/superuser",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 200
        and isinstance(response.json(), list)
        and len(response.json()) == 0
    )

    jwt_two = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-plans/name/test_6/superuser", headers={"Authorization": jwt_two}
    )
    assert response.status_code == 403


def test_can_add_training_unit_to_training_plan(test_client, valid_jwt_token):
    # training unit doesn't exist
    response = test_client.put(
        "/training-plans/1/training-units/1/add",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    test_client.post(
        "/training-units/",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test", "description": "test"},
    )

    response = test_client.put(
        "/training-plans/1/training-units/1/add",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 200
        and response.json()["id"] == 1
        and len(response.json()["training_units"]) == 1
    )
    assert (
        response.json()["training_units"][0]["id"] == 1
        and response.json()["training_units"][0]["name"] == "test"
    )

    response = test_client.put(
        "/training-plans/1/training-units/1/add",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 409

    response = test_client.put(
        "/training-plans/551/training-units/1/add",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    response = test_client.put(
        "/training-plans/6/training-units/1/add",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 200
        and response.json()["id"] == 6
        and len(response.json()["training_units"]) == 1
    )
    assert (
        response.json()["training_units"][0]["id"] == 1
        and response.json()["training_units"][0]["name"] == "test"
    )

    jwt_two = "Bearer " + create_access_token(2)
    response = test_client.put(
        "/training-plans/7/training-units/1/add",
        headers={"Authorization": jwt_two},
    )
    assert (
        response.status_code == 200
        and response.json()["id"] == 7
        and len(response.json()["training_units"]) == 1
    )
    assert (
        response.json()["training_units"][0]["id"] == 1
        and response.json()["training_units"][0]["name"] == "test"
    )

    response = test_client.put(
        "/training-plans/3/training-units/1/add",
        headers={"Authorization": jwt_two},
    )
    assert response.status_code == 403


def test_can_get_training_units_from_training_plan(test_client, valid_jwt_token):
    response = test_client.get(
        "/training-plans/1/training-units",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and len(response.json()) == 0

    jwt_two = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-plans/6/training-units",
        headers={"Authorization": jwt_two},
    )
    assert response.status_code == 200 and len(response.json()) == 0

    response = test_client.get(
        "/training-plans/2/training-units",
        headers={"Authorization": jwt_two},
    )
    assert response.status_code == 403

    response = test_client.get(
        "/training-plans/33/training-units",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404


def test_can_remove_training_unit_from_training_plan(test_client, valid_jwt_token):
    response = test_client.put(
        "/training-plans/1/training-units/1/remove",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    test_client.post(
        "/training-units/",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test", "description": "test"},
    )

    response = test_client.put(
        "/training-plans/1/training-units/1/add",
        headers={"Authorization": valid_jwt_token},
    )

    response = test_client.put(
        "/training-plans/1/training-units/1/remove",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200

    response = test_client.put(
        "/training-plans/1/training-units/2/remove",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    jwt_two = "Bearer " + create_access_token(2)
    response = test_client.put(
        "/training-plans/2/training-units/1/remove",
        headers={"Authorization": jwt_two},
    )
    assert response.status_code == 403
