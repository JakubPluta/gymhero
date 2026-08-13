def test_can_login_for_access_token(test_client, first_active_superuser):
    response = test_client.post(
        "/api/v1/auth/login", data={"username": "admin@admin.com", "password": "admin"}
    )
    data = response.json()
    assert (
        "access_token" in data
        and "refresh_token" in data
        and data["token_type"] == "bearer"
        and response.status_code == 200
    )


def test_cant_login_for_wrong_password(test_client, first_active_superuser):
    response = test_client.post(
        "/api/v1/auth/login", data={"username": "admin@admin.com", "password": "wrong"}
    )
    assert (
        response.status_code == 400
        and response.json()["detail"] == "Incorrect email or password"
    )


def test_cant_login_for_wrong_username(test_client, first_active_superuser):
    response = test_client.post(
        "/api/v1/auth/login", data={"username": "wrong@admin.com", "password": "admin"}
    )
    assert (
        response.status_code == 400
        and response.json()["detail"] == "Incorrect email or password"
    )


def test_cant_login_if_not_active_user(test_client, first_inactive_user):
    response = test_client.post(
        "/api/v1/auth/login", data={"username": "admin@admin.com", "password": "admin"}
    )
    assert response.status_code == 400 and response.json()["detail"] == "Inactive user"


def test_can_register(test_client):
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@admin.com",
            "password": "adminpass1",
            "full_name": "Admin",
        },
    )
    assert response.status_code == 201 and response.json() == {
        "message": "User created successfully"
    }


def test_cannot_register_with_short_password(test_client):
    response = test_client.post(
        "/api/v1/auth/register",
        json={"email": "admin@admin.com", "password": "short", "full_name": "Admin"},
    )
    assert response.status_code == 422


def test_cannot_register_with_invalid_email(test_client):
    response = test_client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "adminpass1"},
    )
    assert response.status_code == 422


def test_cannot_register_if_user_exists(test_client, first_active_superuser):
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@admin.com",
            "password": "adminpass1",
            "full_name": "Admin",
        },
    )
    assert (
        response.status_code == 409
        and response.json()["detail"]
        == "The user with this admin@admin.com already exists in the system"
    )


def _login(test_client) -> dict:
    return test_client.post(
        "/api/v1/auth/login", data={"username": "admin@admin.com", "password": "admin"}
    ).json()


def test_refresh_returns_new_access_token(test_client, first_active_superuser):
    tokens = _login(test_client)
    response = test_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    data = response.json()
    assert (
        response.status_code == 200
        and "access_token" in data
        and data["token_type"] == "bearer"
    )


def test_refresh_rejects_access_token(test_client, first_active_superuser):
    tokens = _login(test_client)
    response = test_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert response.status_code == 401


def test_refresh_rejects_invalid_token(test_client):
    response = test_client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-token"})
    assert response.status_code == 401
