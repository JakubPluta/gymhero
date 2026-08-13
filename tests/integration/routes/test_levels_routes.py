from scripts.core.seed import seed_superuser
from scripts.core.users import get_or_create_user


def test_can_get_many_levels(test_client, seed_levels, initial_levels):
    response = test_client.get("/api/v1/levels/all")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert [level["name"] for level in data["items"]] == initial_levels


def test_can_get_many_levels_with_pagination(test_client, seed_levels, initial_levels):
    response = test_client.get("/api/v1/levels/all", params={"skip": 1, "limit": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1

    response = test_client.get("/api/v1/levels/all", params={"skip": 100, "limit": 1})
    assert response.status_code == 200
    assert response.json()["items"] == []

    # with pytest.raises(Exception):
    response = test_client.get("/api/v1/levels/all", params={"skip": -10, "limit": 5})
    assert (
        response.status_code == 422
        and response.json()["detail"][0]["msg"]
        == "Input should be greater than or equal to 0"
    )


def test_can_get_one_level(test_client, seed_levels, initial_levels):
    response = test_client.get(f"/api/v1/levels/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == initial_levels[0]


def test_can_get_one_level_by_name(test_client, seed_levels, initial_levels):
    response = test_client.get(f"/api/v1/levels/name/{initial_levels[0]}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == initial_levels[0]


def test_should_return_404_when_level_not_found(test_client):
    response = test_client.get(f"/api/v1/levels/100")
    assert response.status_code == 404
    assert response.json()["detail"] == "Level with id 100 not found"


def test_should_return_404_when_level_not_found_by_name(test_client):
    response = test_client.get(f"/api/v1/levels/name/abc")
    assert response.status_code == 404
    assert response.json()["detail"] == "Level with name abc not found"


def test_should_not_have_access_to_create_level(test_client, valid_jwt_token):
    response = test_client.post("/api/v1/levels", json={"name": "test", "description": "test"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    response = test_client.post(
        "/api/v1/levels",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404 and response.json()["detail"] == "User not found"


def test_should_create_level(test_client, valid_jwt_token):
    seed_superuser("test")
    response = test_client.post(
        "/api/v1/levels",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 201 and response.json()["name"] == "test"


def test_cannot_create_level_if_already_exists(
    test_client, valid_jwt_token, seed_levels
):
    seed_superuser("test")
    response = test_client.post(
        "/api/v1/levels",
        json={"name": "Beginner", "description": "Beginner"},
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 409
        and response.json()["detail"] == "Level with name Beginner already exists"
    )


def test_cannot_create_level_if_not_super_user(
    test_client, get_test_db, valid_jwt_token
):
    u = get_or_create_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    response = test_client.post(
        "/api/v1/levels",
        json={"name": "Beginner", "description": "Beginner"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.json()["detail"] == "The user does not have enough privileges"


def test_cannot_delete_level_if_not_super_user(
    test_client, get_test_db, valid_jwt_token
):
    u = get_or_create_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    response = test_client.delete(
        "/api/v1/levels/1",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.json()["detail"] == "The user does not have enough privileges"


def test_can_delete_level(test_client, seed_levels, valid_jwt_token):
    seed_superuser("test")
    response = test_client.delete(
        "/api/v1/levels/1",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 204


def test_cannot_delete_level_if_not_found(test_client, seed_levels, valid_jwt_token):
    seed_superuser("test")
    response = test_client.delete(
        "/api/v1/levels/34343",
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 404
        and response.json()["detail"] == "Level with id 34343 not found. Cannot delete."
    )


def test_delete_level_db_error_returns_clean_500_without_leak(
    test_client, valid_jwt_token, mocker
):
    class User:
        def __init__(self, is_superuser):
            self.id = 34343
            self.is_superuser = is_superuser

    mocker.patch(
        "gymhero.crud.base.CRUDRepository.get_one", return_value=User(is_superuser=True)
    )
    seed_superuser("test")
    response = test_client.delete(
        "/api/v1/levels/34343",
        headers={"Authorization": valid_jwt_token},
    )
    # An unexpected DB error is mapped to a generic 500 by the single error
    # handler; the raw exception detail must never leak to the client.
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert "Error:" not in response.json()["detail"]


def test_cannot_update_level_if_not_super_user(
    test_client, get_test_db, valid_jwt_token
):
    u = get_or_create_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    response = test_client.put(
        "/api/v1/levels/1",
        headers={"Authorization": valid_jwt_token},
        json={"name": "Beginner", "description": "Beginner"},
    )
    assert (
        response.status_code == 403
        and response.json()["detail"] == "The user does not have enough privileges"
    )


def test_cannot_update_level_if_not_exists(test_client, get_test_db, valid_jwt_token):
    seed_superuser("test")
    response = test_client.put(
        "/api/v1/levels/1",
        headers={"Authorization": valid_jwt_token},
        json={"name": "Beginner", "description": "Beginner"},
    )
    assert response.json()["detail"] == "Level with id 1 not found. Cannot update."
    assert response.status_code == 404


def test_can_update_level(test_client, seed_levels, valid_jwt_token):
    seed_superuser("test")
    response = test_client.put(
        "/api/v1/levels/1",
        headers={"Authorization": valid_jwt_token},
        json={"name": "Updated Beginner", "description": "Updated Beginner"},
    )
    assert response.status_code == 200 and response.json()["name"] == "Updated Beginner"


def test_update_level_db_error_returns_clean_500_without_leak(
    test_client, valid_jwt_token, mocker
):
    class User:
        def __init__(self, is_superuser):
            self.is_superuser = is_superuser

    mocker.patch(
        "gymhero.crud.base.CRUDRepository.get_one", return_value=User(is_superuser=True)
    )

    response = test_client.put(
        "/api/v1/levels/34343",
        headers={"Authorization": valid_jwt_token},
        json={"name": "Updated Beginner", "description": "Updated Beginner"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert "Error:" not in response.json()["detail"]
