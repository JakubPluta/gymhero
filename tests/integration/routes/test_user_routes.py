from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.models.user import User
from tests.helpers import DEFAULT_PASSWORD, create_user, page_items

_NEW_USER = {
    "email": "new@example.com",
    "password": "password123",
    "full_name": "New",
    "is_superuser": False,
    "is_active": True,
}


async def test_get_users_as_superuser_returns_all(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    await create_user(db)
    await create_user(db)
    response = await client.get("/api/v1/users/all", headers=superuser_headers)
    assert response.status_code == 200
    assert len(page_items(response)) == 3  # two created + the superuser caller


async def test_get_users_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/all")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_users_non_superuser_returns_403(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/users/all", headers=user_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "The user does not have enough privileges"


async def test_get_user_by_id_returns_it(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    target = await create_user(db)
    response = await client.get(f"/api/v1/users/{target.id}", headers=superuser_headers)
    assert response.status_code == 200
    assert response.json()["id"] == target.id


async def test_get_user_by_id_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/users/9999", headers=superuser_headers)
    assert response.status_code == 404


async def test_get_user_by_email_returns_it(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    target = await create_user(db, email="findme@example.com")
    response = await client.get(
        "/api/v1/users/email/findme@example.com", headers=superuser_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == target.id


async def test_get_user_by_email_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.get(
        "/api/v1/users/email/missing@example.com", headers=superuser_headers
    )
    assert response.status_code == 404


async def test_post_user_as_superuser_returns_201(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/users", json=_NEW_USER, headers=superuser_headers
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"


async def test_post_user_duplicate_email_returns_409(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    await create_user(db, email="dup@example.com")
    response = await client.post(
        "/api/v1/users",
        json={**_NEW_USER, "email": "dup@example.com"},
        headers=superuser_headers,
    )
    assert response.status_code == 409


async def test_post_user_invalid_email_returns_422(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/users",
        json={**_NEW_USER, "email": "not-an-email"},
        headers=superuser_headers,
    )
    assert response.status_code == 422


async def test_post_user_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.post("/api/v1/users", json=_NEW_USER)
    assert response.status_code == 401


async def test_post_user_short_password_returns_422(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/users",
        json={**_NEW_USER, "password": "short"},
        headers=superuser_headers,
    )
    assert response.status_code == 422


async def test_put_user_as_superuser_returns_200(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    target = await create_user(db, email="old@example.com")
    response = await client.put(
        f"/api/v1/users/{target.id}",
        json={**_NEW_USER, "email": "updated@example.com"},
        headers=superuser_headers,
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"


async def test_put_user_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.put(
        "/api/v1/users/9999", json=_NEW_USER, headers=superuser_headers
    )
    assert response.status_code == 404


async def test_put_user_rehashes_password(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    # Regression: an admin password change must actually re-hash and persist,
    # not silently no-op through the generic repo.
    target = await create_user(db, email="pwchange@example.com")
    response = await client.put(
        f"/api/v1/users/{target.id}",
        json={**_NEW_USER, "email": "pwchange@example.com", "password": "new-password-123"},
        headers=superuser_headers,
    )
    assert response.status_code == 200

    new_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "pwchange@example.com", "password": "new-password-123"},
    )
    assert new_login.status_code == 200

    old_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "pwchange@example.com", "password": DEFAULT_PASSWORD},
    )
    assert old_login.status_code == 400


async def test_delete_user_as_superuser_returns_204(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    target = await create_user(db)
    response = await client.delete(
        f"/api/v1/users/{target.id}", headers=superuser_headers
    )
    assert response.status_code == 204


async def test_delete_user_self_returns_403(
    client: AsyncClient, superuser: User, superuser_headers: dict[str, str]
) -> None:
    response = await client.delete(
        f"/api/v1/users/{superuser.id}", headers=superuser_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot delete yourself"


async def test_delete_user_non_superuser_returns_403(
    client: AsyncClient, user_headers: dict[str, str], db: AsyncSession
) -> None:
    target = await create_user(db)
    response = await client.delete(
        f"/api/v1/users/{target.id}", headers=user_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "The user does not have enough privileges"


async def test_delete_user_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.delete("/api/v1/users/9999", headers=superuser_headers)
    assert response.status_code == 404
