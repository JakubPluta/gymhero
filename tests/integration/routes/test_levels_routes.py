import pytest
from fastapi.exceptions import HTTPException, RequestValidationError
from scripts.core._initsu import seed_superuser


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
