def test_can_login_for_access_token(test_client, first_active_superuser):
    response = test_client.post(
        "/auth/login", data={"username": "admin@admin.com", "password": "admin"}
    )
    data = response.json()
    assert (
        "access_token" in data
        and data["token_type"] == "bearer"
        and response.status_code == 200
    )


def test_cant_login_for_wrong_password(test_client, first_active_superuser):
    response = test_client.post(
        "/auth/login", data={"username": "admin@admin.com", "password": "wrong"}
    )
    assert (
        response.status_code == 400
        and response.json()["detail"] == "Incorrect email or password"
    )


def test_cant_login_for_wrong_username(test_client, first_active_superuser):
    response = test_client.post(
        "/auth/login", data={"username": "wrong@admin.com", "password": "admin"}
    )
    assert (
        response.status_code == 400
        and response.json()["detail"] == "Incorrect email or password"
    )


def test_cant_login_if_not_active_user(test_client, first_incative_user):
    response = test_client.post(
        "/auth/login", data={"username": "admin@admin.com", "password": "admin"}
    )
    assert response.status_code == 400 and response.json()["detail"] == "Inactive user"


def test_can_register(test_client):
    response = test_client.post(
        "/auth/register",
        json={
            "email": "admin@admin.com",
            "password": "admin",
            "full_name": "Admin",
            "is_superuser": True,
            "is_active": True,
        },
    )
    assert response.status_code == 201 and response.json() == {
        "message": "User created successfully"
    }


def test_cannot_register_if_user_exists(test_client, first_active_superuser):
    response = test_client.post(
        "/auth/register",
        json={
            "email": "admin@admin.com",
            "password": "admin",
            "full_name": "Admin",
            "is_superuser": True,
            "is_active": True,
        },
    )
    assert (
        response.status_code == 409
        and response.json()["detail"]
        == "The user with this admin@admin.com already exists in the system"
    )
