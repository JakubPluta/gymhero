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
