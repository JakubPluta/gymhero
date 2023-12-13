import pytest
from scripts.core.utils import _create_first_user


@pytest.fixture
def seed_users(get_test_db):
    _create_first_user(get_test_db, "admin@admin.com", "admin", "Admin", True, True)
    _create_first_user(get_test_db, "user1@test.com", "user1", "User1", False, True)
    _create_first_user(get_test_db, "user2@test.com", "user2", "User2", False, True)


def test_cant_get_all_user_if_not_superuser(test_client):
    response = test_client.get("/users/all")
    assert response.status_code == 401


def test_can_get_all_user(test_client, seed_users, valid_jwt_token):
    response = test_client.get("/users/all", headers={"Authorization": valid_jwt_token})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_cant_get_all_user_if_not_authenticated(test_client):
    response = test_client.get("/users/all")
    assert response.status_code == 401


def test_can_get_user_by_id(test_client, seed_users, valid_jwt_token):
    response = test_client.get("/users/2", headers={"Authorization": valid_jwt_token})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2

    response = test_client.get("/users/100")
    assert response.status_code == 401


def test_can_get_user_by_name(test_client, seed_users, valid_jwt_token):
    response = test_client.get(
        "/users/email/user2@test.com", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 3

    response = test_client.get("/users/email/user2@test.com")
    assert response.status_code == 401


def test_can_create_user(test_client, get_test_db, valid_jwt_token):
    _create_first_user(get_test_db, "admin@test.com", "admin", "admin", True, True)

    response = test_client.post(
        "/users",
        json={
            "email": "test@test.com",
            "password": "test",
            "full_name": "test",
            "is_superuser": False,
            "is_active": True,
        },
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 201

    response = test_client.post(
        "/users",
        json={
            "email": "test@test.com",
            "password": "test",
            "full_name": "test",
            "is_superuser": False,
            "is_active": True,
        },
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 409

    response = test_client.post(
        "/users",
        json={
            "email": "tes1t@test.com",
            "password": "test",
            "full_name": "test",
            "is_superuser": False,
            "is_active": True,
        },
    )

    assert response.status_code == 401
