from httpx import AsyncClient

from gymhero.models.user import User
from tests.helpers import DEFAULT_PASSWORD


async def _login(client: AsyncClient, user: User) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": DEFAULT_PASSWORD},
    )
    return response.json()


async def test_login_returns_token_pair(
    client: AsyncClient, regular_user: User
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": regular_user.email, "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


async def test_login_wrong_password_returns_400(
    client: AsyncClient, regular_user: User
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": regular_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"


async def test_login_unknown_user_returns_400(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "ghost@example.com", "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"


async def test_login_inactive_user_returns_400(
    client: AsyncClient, inactive_user: User
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": inactive_user.email, "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"


async def test_register_creates_user_returns_201(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "password123", "full_name": "New"},
    )
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}


async def test_register_then_login_succeeds(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "roundtrip@example.com", "password": "password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "roundtrip@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_register_short_password_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "x@example.com", "password": "short", "full_name": "X"},
    )
    assert response.status_code == 422


async def test_register_invalid_email_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )
    assert response.status_code == 422


async def test_register_existing_email_returns_409(
    client: AsyncClient, regular_user: User
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": regular_user.email, "password": "password123", "full_name": "D"},
    )
    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == f"The user with this {regular_user.email} already exists in the system"
    )


async def test_refresh_returns_new_access_token(
    client: AsyncClient, regular_user: User
) -> None:
    tokens = await _login(client, regular_user)
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


async def test_refresh_rejects_access_token(
    client: AsyncClient, regular_user: User
) -> None:
    tokens = await _login(client, regular_user)
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert response.status_code == 401


async def test_refresh_rejects_garbage_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "not-a-token"}
    )
    assert response.status_code == 401


async def test_refresh_missing_body_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/refresh", json={})
    assert response.status_code == 422
