import pytest

from gymhero.crud.training_unit import training_unit_crud
from gymhero.models.training_unit import TrainingUnit
from gymhero.schemas.training_unit import TrainingUnitCreate
from gymhero.security import create_access_token
from scripts.core.utils import _create_first_user


@pytest.fixture(autouse=True, scope="function")
def seed_training_units(get_test_db):
    u = _create_first_user(get_test_db, "admin@admin.com", "admin", "Admin", True, True)

    training_units = [
        TrainingUnitCreate(name=f"test_{i}", description=f"test_{i}") for i in range(5)
    ]

    for training_unit in training_units:
        training_unit_crud.create_with_owner(get_test_db, training_unit, u.id)

    u2 = _create_first_user(get_test_db, "abc@abc.com", "abc", "abc", False, True)
    training_units = [
        TrainingUnitCreate(name=f"test_{i}", description=f"test_{i}")
        for i in range(6, 9)
    ]

    for training_unit in training_units:
        training_unit_crud.create_with_owner(get_test_db, training_unit, u2.id)


def test_get_all_training_units(test_client, valid_jwt_token):
    response = test_client.get(
        "/training-units/all?skip=0&limit=3", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200 and len(response.json()) == 3

    response = test_client.get(
        "/training-units/all?skip=-10&limit=-5",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 422

    response = test_client.get("/training-units/all?skip=0&limit=10000")
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )


def test_get_all_training_units_for_owner(test_client, valid_jwt_token):
    response = test_client.get(
        "/training-units/all/my?skip=0&limit=3",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and len(response.json()) == 3


def test_get_one_training_unit(test_client, get_test_db, valid_jwt_token):
    response = test_client.get(
        "/training-units/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200 and response.json()["id"] == 1

    response = test_client.get(
        "/training-units/10", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    # Test with JWT of another user
    jwt_2 = "Bearer " + create_access_token(2)
    response = test_client.get("/training-units/3", headers={"Authorization": jwt_2})
    assert response.status_code == 404

    response = test_client.get("/training-units/6", headers={"Authorization": jwt_2})
    assert response.status_code == 200

    response = test_client.get(
        "/training-units/name/test_0", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200 and response.json()["name"] == "test_0"

    response = test_client.get(
        "/training-units/name/test200", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    # Test with JWT of another user
    jwt_2 = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-units/name/test_0", headers={"Authorization": jwt_2}
    )
    assert response.status_code == 404

    response = test_client.get(
        "/training-units/name/test_6", headers={"Authorization": jwt_2}
    )
    assert response.status_code == 200


def test_get_training_units_for_superuser(test_client, get_test_db, valid_jwt_token):
    response = test_client.get(
        "/training-units/name/test_0/superuser",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and isinstance(response.json(), list)

    response = test_client.get(
        "/training-units/name/test_6/superuser",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and isinstance(response.json(), list)

    jwt_2 = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-units/name/test_0/superuser", headers={"Authorization": jwt_2}
    )
    assert (
        response.status_code == 403
        and response.json()["detail"] == "The user does not have enough privileges"
    )


def test_can_create_training_unit(test_client, valid_jwt_token):
    response = test_client.post(
        "/training-units/",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test", "description": "test"},
    )
    assert response.status_code == 201 and response.json()["name"] == "test"


def test_can_create_training_unit(test_client, valid_jwt_token):
    response = test_client.post(
        "/training-units/",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test_0", "description": "test"},
    )
    assert response.status_code == 409


def test_can_update_training_unit(test_client, valid_jwt_token):
    response = test_client.put(
        "/training-units/1",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test", "description": "test"},
    )
    assert response.status_code == 200 and response.json()["name"] == "test"

    response = test_client.put(
        "/training-units/22",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test", "description": "test"},
    )
    assert response.status_code == 404

    another_token = "Bearer " + create_access_token(2)
    response = test_client.put(
        "/training-units/1",
        headers={"Authorization": another_token},
        json={"name": "test", "description": "test"},
    )
    assert response.status_code == 403

    response = test_client.put(
        "/training-units/6",
        headers={"Authorization": valid_jwt_token},
        json={"name": "test", "description": "test"},
    )
    assert response.status_code == 200 and response.json()["name"] == "test"


def test_can_delete_training_unit(test_client, valid_jwt_token):
    response = test_client.delete(
        "/training-units/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200

    response = test_client.delete(
        "/training-units/22", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404

    another_token = "Bearer " + create_access_token(2)
    response = test_client.delete(
        "/training-units/2", headers={"Authorization": another_token}
    )
    assert response.status_code == 403

    response = test_client.delete(
        "/training-units/6", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200


def test_can_add_exercise_to_training_unit(
    test_client, valid_jwt_token, seed_test_database
):
    response = test_client.put(
        "/training-units/1/exercises/1/add",
        headers={"Authorization": valid_jwt_token},
    )

    exercise_response = test_client.get(
        "/exercises/1", headers={"Authorization": valid_jwt_token}
    )
    exercises = response.json()["exercises"]
    assert (
        response.status_code == 200
        and exercises == [exercise_response.json()]
        and len(exercises) == 1
    )

    response = test_client.put(
        "/training-units/1/exercises/1/add",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 409

    response = test_client.put(
        "/training-units/55/exercises/1/add",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    response = test_client.put(
        "/training-units/1/exercises/34341/add",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    jwt_token = "Bearer " + create_access_token(2)

    response = test_client.put(
        "/training-units/1/exercises/1/add",
        headers={"Authorization": jwt_token},
    )
    assert response.status_code == 403


def test_can_remove_exercise_from_training_unit(
    test_client, valid_jwt_token, seed_test_database
):
    response = test_client.put(
        "/training-units/1/exercises/1/add",
        headers={"Authorization": valid_jwt_token},
    )
    exercise_response = test_client.get(
        "/exercises/1", headers={"Authorization": valid_jwt_token}
    )

    assert response.json()["exercises"] == [exercise_response.json()]

    response = test_client.put(
        "/training-units/1/exercises/1/remove",
        headers={"Authorization": valid_jwt_token},
    )

    exercises = response.json()["exercises"]
    assert response.status_code == 200 and exercises == [] and len(exercises) == 0

    response = test_client.put(
        "/training-units/1/exercises/55555/remove",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    response = test_client.put(
        "/training-units/51/exercises/1/remove",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    jwt_token_u2 = "Bearer " + create_access_token(2)
    response = test_client.put(
        "/training-units/1/exercises/1/remove",
        headers={"Authorization": jwt_token_u2},
    )
    assert response.status_code == 403

    response = test_client.put(
        "/training-units/1/exercises/2/remove",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 409


def test_can_get_exercises_in_training_unit(
    test_client, valid_jwt_token, seed_test_database
):
    response = test_client.get(
        "/training-units/1/exercises",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and len(response.json()) == 0

    test_client.put(
        "/training-units/1/exercises/2/add",
        headers={"Authorization": valid_jwt_token},
    )

    response = test_client.get(
        "/training-units/1/exercises",
        headers={"Authorization": valid_jwt_token},
    )

    assert response.status_code == 200 and len(response.json()) == 1

    response = test_client.get(
        "/training-units/3242/exercises",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404

    jwt_token_v2 = "Bearer " + create_access_token(2)
    response = test_client.get(
        "/training-units/1/exercises",
        headers={"Authorization": jwt_token_v2},
    )
    assert response.status_code == 403
