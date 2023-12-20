import json
import unittest

import pytest
from fastapi.exceptions import HTTPException, RequestValidationError

from scripts.core._initsu import seed_superuser
from scripts.core.utils import _create_first_user


def test_can_get_many_levels(test_client, seed_levels, initial_levels):
    response = test_client.get("/levels/all")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert [level["name"] for level in data] == initial_levels


def test_can_get_many_levels_with_pagination(test_client, seed_levels, initial_levels):
    response = test_client.get("/levels/all", params={"skip": 1, "limit": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    response = test_client.get("/levels/all", params={"skip": 100, "limit": 1})
    assert response.status_code == 200
    assert response.json() == []

    # with pytest.raises(Exception):
    response = test_client.get("/levels/all", params={"skip": -10, "limit": 5})
    assert (
        response.status_code == 422
        and response.json()["detail"][0]["msg"]
        == "Input should be greater than or equal to 0"
    )


def test_can_get_one_level(test_client, seed_levels, initial_levels):
    response = test_client.get(f"/levels/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == initial_levels[0]


def test_can_get_one_level_by_name(test_client, seed_levels, initial_levels):
    response = test_client.get(f"/levels/name/{initial_levels[0]}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == initial_levels[0]


def test_should_return_404_when_level_not_found(test_client):
    response = test_client.get(f"/levels/100")
    assert response.status_code == 404
    assert response.json()["detail"] == "Level with id 100 not found"


def test_should_return_404_when_level_not_found_by_name(test_client):
    response = test_client.get(f"/levels/name/abc")
    assert response.status_code == 404
    assert response.json()["detail"] == "Level with name abc not found"


def test_should_not_have_access_to_create_level(test_client, valid_jwt_token):
    response = test_client.post("/levels", json={"name": "test", "description": "test"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    response = test_client.post(
        "/levels",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404 and response.json()["detail"] == "User not found"


def test_should_create_level(test_client, valid_jwt_token):
    seed_superuser("test")
    response = test_client.post(
        "/levels",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 201 and response.json()["name"] == "test"


def test_cannot_create_level_if_already_exists(
    test_client, valid_jwt_token, seed_levels
):
    seed_superuser("test")
    response = test_client.post(
        "/levels",
        json={"name": "Beginner", "description": "Beginner"},
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 500
        and response.json()["detail"]
        == "Couldn't create level. Level with name: Beginner already exists"
    )


def test_cannot_create_level_if_not_super_user(
    test_client, get_test_db, valid_jwt_token
):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    response = test_client.post(
        "/levels",
        json={"name": "Beginner", "description": "Beginner"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.json()["detail"] == "The user does not have enough privileges"


def test_cannot_delete_level_if_not_super_user(
    test_client, get_test_db, valid_jwt_token
):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    response = test_client.delete(
        "/levels/1",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.json()["detail"] == "The user does not have enough privileges"


def test_can_delete_level(test_client, seed_levels, valid_jwt_token):
    seed_superuser("test")
    response = test_client.delete(
        "/levels/1",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200


def test_cannot_delete_level_if_not_found(test_client, seed_levels, valid_jwt_token):
    seed_superuser("test")
    response = test_client.delete(
        "/levels/34343",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 404
        and response.json()["detail"] == "Level with id 34343 not found. Cannot delete."
    )


def test_should_rise_internal_error_while_delete(test_client, valid_jwt_token, mocker):
    class User:
        def __init__(self, is_superuser):
            self.is_superuser = is_superuser

    mocker.patch(
        "gymhero.crud.base.CRUDRepository.get_one", return_value=User(is_superuser=True)
    )
    seed_superuser("test")
    response = test_client.delete(
        "/levels/34343",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 500
        and "Couldn't delete level with id 34343. Error:" in response.json()["detail"]
    )


def test_cannot_update_level_if_not_super_user(
    test_client, get_test_db, valid_jwt_token
):
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    response = test_client.put(
        "/levels/1",
        headers={"Authorization": valid_jwt_token},
        content=json.dumps({"name": "Beginner", "description": "Beginner"}),
    )
    assert (
        response.status_code == 403
        and response.json()["detail"] == "The user does not have enough privileges"
    )


def test_cannot_update_level_if_not_exists(test_client, get_test_db, valid_jwt_token):
    seed_superuser("test")
    response = test_client.put(
        "/levels/1",
        headers={"Authorization": valid_jwt_token},
        content=json.dumps({"name": "Beginner", "description": "Beginner"}),
    )
    assert response.json()["detail"] == "Level with id 1 not found. Cannot update."
    assert response.status_code == 404


def test_can_update_level(test_client, seed_levels, valid_jwt_token):
    seed_superuser("test")
    response = test_client.put(
        "/levels/1",
        headers={"Authorization": valid_jwt_token},
        content=json.dumps(
            {"name": "Updated Beginner", "description": "Updated Beginner"}
        ),
    )
    assert response.status_code == 200 and response.json()["name"] == "Updated Beginner"


def test_should_rise_internal_error_while_updating(
    test_client, valid_jwt_token, mocker
):
    class User:
        def __init__(self, is_superuser):
            self.is_superuser = is_superuser

    mocker.patch(
        "gymhero.crud.base.CRUDRepository.get_one", return_value=User(is_superuser=True)
    )

    response = test_client.put(
        "/levels/34343",
        headers={"Authorization": valid_jwt_token},
        content=json.dumps(
            {"name": "Updated Beginner", "description": "Updated Beginner"}
        ),
    )
    assert (
        response.status_code == 500
        and "Couldn't update level with id 34343. Error:" in response.json()["detail"]
    )
