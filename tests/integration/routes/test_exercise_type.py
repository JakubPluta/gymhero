import pytest

from scripts.core.utils import _create_first_user


def test_get_all_exercise_types(
    test_client, get_test_db, seed_exercise_types, valid_jwt_token
):
    _create_first_user(get_test_db, "admin@admin.com", "admin", "Admin", True, True)

    response = test_client.get(
        "/exercise-types/all",
        params={"limit": 3, "skip": 0},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    response = test_client.get("/exercise-types/all", params={"limit": 1, "skip": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_one_exercise_type(
    test_client, get_test_db, seed_exercise_types, valid_jwt_token
):
    _create_first_user(get_test_db, "admin@admin.com", "admin", "Admin", True, True)

    response = test_client.get(
        "/exercise-types/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

    response = test_client.get(
        "/exercise-types/name/Strength", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Strength"

    response = test_client.get(
        "/exercise-types/200", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise type with id 200 not found"

    response = test_client.get(
        "/exercise-types/name/abc", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise type with name abc not found"


def test_can_create_exercise_type(test_client, get_test_db, valid_jwt_token):
    _create_first_user(get_test_db, "admin@admin.com", "admin", "Admin", True, True)

    response = test_client.post(
        "/exercise-types",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 201

    response = test_client.post(
        "/body-parts",
        json={"name": "test", "description": "test"},
    )
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )

    response = test_client.post(
        "/exercise-types",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 409
        and response.json()["detail"] == "Exercise type with name test already exists"
    )


def test_can_delete_exercise_type(
    test_client, get_test_db, seed_exercise_types, valid_jwt_token
):
    _create_first_user(get_test_db, "admin@admin.com", "admin", "Admin", True, True)

    response = test_client.delete(
        "/exercise-types/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200

    response = test_client.delete(
        "/exercise-types/100", headers={"Authorization": valid_jwt_token}
    )
    assert (
        response.status_code == 404
        and response.json()["detail"] == "Exercise type with id 100 not found."
    )

    response = test_client.delete("/exercise-types/1")
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )


def test_can_update_exercise_type(
    test_client, get_test_db, seed_exercise_types, valid_jwt_token
):
    _create_first_user(get_test_db, "admin@admin.com", "admin", "Admin", True, True)

    response = test_client.put(
        "/exercise-types/1",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200

    response = test_client.put(
        "/exercise-types/100",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 404
        and response.json()["detail"] == "Exercise type with id 100 not found."
    )
