import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.models.exercise import ExerciseType
from gymhero.models.user import User
from tests.helpers import auth_headers, create_exercise_type, page_items


async def test_get_exercise_types_returns_paginated_items(
    client: AsyncClient, seeded_exercise_types: list[ExerciseType]
) -> None:
    response = await client.get(
        "/api/v1/exercise-types/all", params={"skip": 0, "limit": 3}
    )
    assert response.status_code == 200
    assert len(page_items(response)) == 3


async def test_get_exercise_types_reads_are_public(
    client: AsyncClient, seeded_exercise_types: list[ExerciseType]
) -> None:
    response = await client.get(
        "/api/v1/exercise-types/all", params={"skip": 1, "limit": 1}
    )
    assert response.status_code == 200
    assert len(page_items(response)) == 1


async def test_get_exercise_type_by_id_returns_it(
    client: AsyncClient, seeded_exercise_types: list[ExerciseType]
) -> None:
    target = seeded_exercise_types[0]
    response = await client.get(f"/api/v1/exercise-types/{target.id}")
    assert response.status_code == 200
    assert response.json()["id"] == target.id


async def test_get_exercise_type_by_name_returns_it(
    client: AsyncClient, seeded_exercise_types: list[ExerciseType]
) -> None:
    target = seeded_exercise_types[0]
    response = await client.get(f"/api/v1/exercise-types/name/{target.name}")
    assert response.status_code == 200
    assert response.json()["name"] == target.name


async def test_get_exercise_type_by_id_missing_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/exercise-types/200")
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise type with id 200 not found"


async def test_get_exercise_type_by_name_missing_returns_404(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/exercise-types/name/abc")
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise type with name abc not found"


async def test_post_exercise_type_as_superuser_returns_201(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/exercise-types",
        json={"name": "Plyometric", "description": "explosive"},
        headers=superuser_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Plyometric"


async def test_post_exercise_type_duplicate_name_returns_409(
    client: AsyncClient, superuser_headers: dict[str, str], db: AsyncSession
) -> None:
    await create_exercise_type(db, name="Plyometric")
    response = await client.post(
        "/api/v1/exercise-types",
        json={"name": "Plyometric", "description": "explosive"},
        headers=superuser_headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Exercise type with name Plyometric already exists"


async def test_post_exercise_type_missing_name_returns_422(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/exercise-types", json={"description": "d"}, headers=superuser_headers
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("authenticated", "expected_status"),
    [(False, 401), (True, 403)],
    ids=["anonymous", "non_superuser"],
)
async def test_post_exercise_type_without_privileges_is_rejected(
    client: AsyncClient,
    regular_user: User,
    authenticated: bool,
    expected_status: int,
) -> None:
    headers = auth_headers(regular_user) if authenticated else {}
    response = await client.post(
        "/api/v1/exercise-types",
        json={"name": "Plyometric", "description": "explosive"},
        headers=headers,
    )
    assert response.status_code == expected_status


async def test_put_exercise_type_as_superuser_returns_200(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    seeded_exercise_types: list[ExerciseType],
) -> None:
    target = seeded_exercise_types[0]
    response = await client.put(
        f"/api/v1/exercise-types/{target.id}",
        json={"name": "Endurance", "description": "long"},
        headers=superuser_headers,
    )
    assert response.status_code == 200


async def test_put_exercise_type_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.put(
        "/api/v1/exercise-types/100",
        json={"name": "Endurance", "description": "long"},
        headers=superuser_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise type with id 100 not found."


async def test_delete_exercise_type_as_superuser_returns_204(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    seeded_exercise_types: list[ExerciseType],
) -> None:
    target = seeded_exercise_types[0]
    response = await client.delete(
        f"/api/v1/exercise-types/{target.id}", headers=superuser_headers
    )
    assert response.status_code == 204


async def test_delete_exercise_type_missing_returns_404(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    response = await client.delete(
        "/api/v1/exercise-types/100", headers=superuser_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise type with id 100 not found."


async def test_delete_exercise_type_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/exercise-types/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
