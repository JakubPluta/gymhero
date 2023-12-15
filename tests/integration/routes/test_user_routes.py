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


def test_can_update_user(test_client, get_test_db, valid_jwt_token):
    _create_first_user(get_test_db, "admin@test.com", "admin", "admin", True, True)

    response = test_client.put(
        "/users/1",
        json={
            "email": "test@test.com",
            "password": "test",
            "full_name": "test",
            "is_superuser": False,
            "is_active": True,
        },
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and response.json()["email"] == "test@test.com"


def test_can_delete_user(test_client, get_test_db, valid_jwt_token):
    _create_first_user(get_test_db, "admin@test.com", "admin", "admin", True, True)
    _create_first_user(get_test_db, "test@test.com", "test", "test", False, True)

    response = test_client.delete(
        "/users/2",
        headers={"Authorization": valid_jwt_token},
    )

    assert response.status_code == 200


def test_cant_delete_user_if_not_superuser(test_client, get_test_db, valid_jwt_token):
    _create_first_user(get_test_db, "admin@test.com", "admin", "admin", False, True)
    _create_first_user(get_test_db, "test@test.com", "test", "test", False, True)

    response = test_client.delete(
        "/users/1",
        headers={"Authorization": valid_jwt_token},
    )

    assert (
        response.status_code == 403
        and response.json()["detail"] == "The user does not have enough privileges"
    )


def test_cannot_delete_myself(test_client, get_test_db, valid_jwt_token):
    _create_first_user(get_test_db, "admin@test.com", "admin", "admin", True, True)

    response = test_client.delete(
        "/users/1",
        headers={"Authorization": valid_jwt_token},
    )

    assert (
        response.status_code == 403
        and response.json()["detail"] == "You cannot delete yourself"
    )


def test_cannot_delete_non_existing_user(test_client, valid_jwt_token, get_test_db):
    _create_first_user(get_test_db, "admin@test.com", "admin", "admin", True, True)
    response = test_client.delete(
        "/users/100",
        headers={"Authorization": valid_jwt_token},
    )

    assert response.status_code == 404


def test_cannot_update_non_existing_user(test_client, valid_jwt_token, get_test_db):
    _create_first_user(get_test_db, "admin@test.com", "admin", "admin", True, True)
    response = test_client.put(
        "/users/100",
        json={
            "email": "test@test.com",
            "password": "test",
            "full_name": "test",
            "is_superuser": False,
            "is_active": True,
        },
        headers={"Authorization": valid_jwt_token},
    )

    assert response.status_code == 404


def test_cannot_fetch_non_existing_user(test_client, valid_jwt_token, get_test_db):
    _create_first_user(get_test_db, "admin@test.com", "admin", "admin", True, True)
    response = test_client.get(
        "/users/100",
        headers={"Authorization": valid_jwt_token},
    )

    assert response.status_code == 404

    response = test_client.get(
        "/users/email/test",
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 404
