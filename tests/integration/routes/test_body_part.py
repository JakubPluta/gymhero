import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.models.body_part import BodyPart
from tests.helpers import auth_headers, create_body_part, page_items


async def test_get_body_parts_returns_paginated_items(
    client: AsyncClient, seeded_body_parts: list[BodyPart]
) -> None:
    response = await client.get("/api/v1/body-parts/all", params={"skip": 0, "limit": 3})
    assert response.status_code == 200
    assert len(page_items(response)) == 3


async def test_get_body_parts_reads_are_public(
    client: AsyncClient, seeded_body_parts: list[BodyPart]
) -> None:
    # The reference catalog is intentionally readable without a token.
    response = await client.get("/api/v1/body-parts/all", params={"skip": 1, "limit": 1})
    assert response.status_code == 200
    assert len(page_items(response)) == 1


async def test_get_body_part_by_id_returns_it(
    client: AsyncClient, seeded_body_parts: list[BodyPart]
) -> None:
    target = seeded_body_parts[0]
    response = await client.get(f"/api/v1/body-parts/{target.id}")
    assert response.status_code == 200
    assert response.json()["id"] == target.id
    assert response.json()["name"] == target.name


async def test_get_body_part_by_name_returns_it(
    client: AsyncClient, seeded_body_parts: list[BodyPart]
) -> None:
    target = seeded_body_parts[0]
    response = await client.get(f"/api/v1/body-parts/name/{target.name}")
    assert response.status_code == 200
    assert response.json()["name"] == target.name


async def test_get_body_part_by_id_missing_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/body-parts/100")
    assert response.status_code == 404
    assert response.json()["detail"] == "Body part with id 100 not found"


async def test_get_body_part_by_name_missing_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/body-parts/name/abc")
    assert response.status_code == 404
    assert response.json()["detail"] == "Body part with name abc not found"


async def test_post_body_part_as_superuser_returns_201(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/body-parts",
        json={"name": "Calves", "description": "lower leg"},
        headers=superuser_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Calves"


async def test_post_body_part_duplicate_name_returns_409(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    await create_body_part(db, name="Calves")
    response = await client.post(
        "/api/v1/body-parts",
        json={"name": "Calves", "description": "lower leg"},
        headers=superuser_headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Body part with name Calves already exists"


async def test_post_body_part_missing_name_returns_422(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/body-parts", json={"description": "d"}, headers=superuser_headers
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("authenticated", "expected_status"),
    [(False, 401), (True, 403)],
    ids=["anonymous", "non_superuser"],
)
async def test_post_body_part_without_privileges_is_rejected(
    client: AsyncClient,
    regular_user: object,
    authenticated: bool,
    expected_status: int,
) -> None:
    headers = auth_headers(regular_user) if authenticated else {}
    response = await client.post(
        "/api/v1/body-parts",
        json={"name": "Calves", "description": "lower leg"},
        headers=headers,
    )
    assert response.status_code == expected_status


async def test_put_body_part_as_superuser_returns_200(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    seeded_body_parts: list[BodyPart],
) -> None:
    target = seeded_body_parts[0]
    response = await client.put(
        f"/api/v1/body-parts/{target.id}",
        json={"name": "Quads", "description": "front thigh"},
        headers=superuser_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Quads"


async def test_put_body_part_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.put(
        "/api/v1/body-parts/100",
        json={"name": "Quads", "description": "front thigh"},
        headers=superuser_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Body part with id 100 not found. Cannot update."


async def test_delete_body_part_as_superuser_returns_204(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    seeded_body_parts: list[BodyPart],
) -> None:
    target = seeded_body_parts[0]
    response = await client.delete(
        f"/api/v1/body-parts/{target.id}", headers=superuser_headers
    )
    assert response.status_code == 204


async def test_delete_body_part_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.delete("/api/v1/body-parts/100", headers=superuser_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Body part with id 100 not found. Cannot delete."


async def test_delete_body_part_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/body-parts/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_write_body_part_with_unknown_user_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/body-parts",
        json={"name": "Calves", "description": "lower leg"},
        headers=auth_headers(9999),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
