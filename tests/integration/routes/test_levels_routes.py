import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from gymhero.models.level import Level
from gymhero.models.user import User
from tests.helpers import auth_headers, page_items


async def test_get_levels_returns_paginated_items(
    client: AsyncClient, seeded_levels: list[Level]
) -> None:
    response = await client.get("/api/v1/levels/all")
    assert response.status_code == 200
    assert [item["name"] for item in page_items(response)] == [
        level.name for level in seeded_levels
    ]


async def test_get_levels_pagination_skip_and_limit(
    client: AsyncClient, seeded_levels: list[Level]
) -> None:
    response = await client.get("/api/v1/levels/all", params={"skip": 1, "limit": 1})
    assert response.status_code == 200
    assert len(page_items(response)) == 1

    response = await client.get("/api/v1/levels/all", params={"skip": 100, "limit": 1})
    assert response.status_code == 200
    assert page_items(response) == []


async def test_get_levels_negative_skip_returns_422(client: AsyncClient) -> None:
    response = await client.get("/api/v1/levels/all", params={"skip": -10, "limit": 5})
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "Input should be greater than or equal to 0"
    )


async def test_get_level_by_id_returns_it(
    client: AsyncClient, seeded_levels: list[Level]
) -> None:
    target = seeded_levels[0]
    response = await client.get(f"/api/v1/levels/{target.id}")
    assert response.status_code == 200
    assert response.json()["name"] == target.name


async def test_get_level_by_name_returns_it(
    client: AsyncClient, seeded_levels: list[Level]
) -> None:
    target = seeded_levels[0]
    response = await client.get(f"/api/v1/levels/name/{target.name}")
    assert response.status_code == 200
    assert response.json()["name"] == target.name


async def test_get_level_by_id_missing_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/levels/100")
    assert response.status_code == 404
    assert response.json()["detail"] == "Level with id 100 not found"


async def test_get_level_by_name_missing_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/levels/name/abc")
    assert response.status_code == 404
    assert response.json()["detail"] == "Level with name abc not found"


async def test_post_level_as_superuser_returns_201(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/levels",
        json={"name": "Expert", "description": "Expert"},
        headers=superuser_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Expert"


async def test_post_level_duplicate_name_returns_409(
    client: AsyncClient, superuser_headers: dict[str, str], seeded_levels: list[Level]
) -> None:
    existing = seeded_levels[0].name
    response = await client.post(
        "/api/v1/levels",
        json={"name": existing, "description": existing},
        headers=superuser_headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == f"Level with name {existing} already exists"


@pytest.mark.parametrize(
    ("authenticated", "expected_status", "expected_detail"),
    [
        (False, 401, "Not authenticated"),
        (True, 403, "The user does not have enough privileges"),
    ],
    ids=["anonymous", "non_superuser"],
)
async def test_post_level_without_privileges_is_rejected(
    client: AsyncClient,
    regular_user: User,
    authenticated: bool,
    expected_status: int,
    expected_detail: str,
) -> None:
    headers = auth_headers(regular_user) if authenticated else {}
    response = await client.post(
        "/api/v1/levels", json={"name": "Expert", "description": "d"}, headers=headers
    )
    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail


async def test_post_level_unknown_user_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/levels",
        json={"name": "Expert", "description": "d"},
        headers=auth_headers(9999),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_put_level_as_superuser_returns_200(
    client: AsyncClient, superuser_headers: dict[str, str], seeded_levels: list[Level]
) -> None:
    target = seeded_levels[0]
    response = await client.put(
        f"/api/v1/levels/{target.id}",
        json={"name": "Updated", "description": "Updated"},
        headers=superuser_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


async def test_put_level_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.put(
        "/api/v1/levels/9999",
        json={"name": "Updated", "description": "Updated"},
        headers=superuser_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Level with id 9999 not found. Cannot update."


async def test_delete_level_as_superuser_returns_204(
    client: AsyncClient, superuser_headers: dict[str, str], seeded_levels: list[Level]
) -> None:
    target = seeded_levels[0]
    response = await client.delete(
        f"/api/v1/levels/{target.id}", headers=superuser_headers
    )
    assert response.status_code == 204


async def test_delete_level_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.delete("/api/v1/levels/9999", headers=superuser_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Level with id 9999 not found. Cannot delete."


class _FakeSuperuser:
    id = 4242
    is_superuser = True
    is_active = True


async def test_delete_level_db_error_returns_clean_500_without_leak(
    client: AsyncClient, mocker: MockerFixture
) -> None:
    # get_one now yields a non-Level object, so the delete blows up inside the
    # service; the error handler must map that to a generic 500 with no leak.
    mocker.patch(
        "gymhero.crud.base.CRUDRepository.get_one", return_value=_FakeSuperuser()
    )
    response = await client.delete("/api/v1/levels/4242", headers=auth_headers(4242))
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert "Error:" not in response.json()["detail"]


async def test_update_level_db_error_returns_clean_500_without_leak(
    client: AsyncClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "gymhero.crud.base.CRUDRepository.get_one", return_value=_FakeSuperuser()
    )
    response = await client.put(
        "/api/v1/levels/4242",
        json={"name": "x", "description": "x"},
        headers=auth_headers(4242),
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert "Error:" not in response.json()["detail"]
