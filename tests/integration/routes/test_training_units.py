from dataclasses import dataclass

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.models.training_unit import TrainingUnit
from gymhero.models.user import User
from tests.helpers import create_exercise, create_training_unit, page_items


@dataclass(frozen=True)
class UnitWorld:
    owner: User
    owner_headers: dict[str, str]
    other: User
    other_headers: dict[str, str]
    owner_units: list[TrainingUnit]
    other_units: list[TrainingUnit]


@pytest.fixture
async def world(
    db: AsyncSession,
    superuser: User,
    superuser_headers: dict[str, str],
    other_user: User,
    other_user_headers: dict[str, str],
) -> UnitWorld:
    owner_units = [
        await create_training_unit(db, owner=superuser, name=f"owner-unit-{i}")
        for i in range(5)
    ]
    other_units = [
        await create_training_unit(db, owner=other_user, name=f"other-unit-{i}")
        for i in range(3)
    ]
    return UnitWorld(
        superuser, superuser_headers, other_user, other_user_headers,
        owner_units, other_units,
    )


async def test_get_all_training_units_superuser_paginates(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/all",
        params={"skip": 0, "limit": 3},
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert len(page_items(response)) == 3


async def test_get_all_training_units_negative_params_returns_422(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/all",
        params={"skip": -10, "limit": -5},
        headers=world.owner_headers,
    )
    assert response.status_code == 422


async def test_get_all_training_units_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/training-units/all", params={"skip": 0, "limit": 10}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_all_training_units_non_superuser_returns_403(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/all",
        params={"skip": 0, "limit": 3},
        headers=world.other_headers,
    )
    assert response.status_code == 403


async def test_get_my_training_units_returns_only_owned(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/all/my",
        params={"limit": 10},
        headers=world.other_headers,
    )
    assert response.status_code == 200
    assert len(page_items(response)) == len(world.other_units)


async def test_search_training_units_on_my_filters_by_name(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/all/my",
        params={"q": "other-unit-1"},
        headers=world.other_headers,
    )
    assert response.status_code == 200
    assert [item["name"] for item in page_items(response)] == ["other-unit-1"]
    assert response.json()["total"] == 1


async def test_search_training_units_on_my_scopes_to_owner(
    client: AsyncClient, world: UnitWorld
) -> None:
    # 'owner-unit-*' belong to the superuser; the other user's /my search sees none.
    response = await client.get(
        "/api/v1/training-units/all/my",
        params={"q": "owner-unit"},
        headers=world.other_headers,
    )
    assert page_items(response) == []
    assert response.json()["total"] == 0


async def test_search_training_units_all_superuser_spans_owners(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/all",
        params={"q": "other-unit"},
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["total"] == len(world.other_units)


async def test_get_training_unit_by_id_owner_returns_it(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.get(
        f"/api/v1/training-units/{unit.id}", headers=world.owner_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == unit.id


async def test_get_training_unit_by_id_missing_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/999999", headers=world.owner_headers
    )
    assert response.status_code == 404


async def test_get_training_unit_by_id_not_owner_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.get(
        f"/api/v1/training-units/{unit.id}", headers=world.other_headers
    )
    assert response.status_code == 404


async def test_get_training_unit_by_name_owner_returns_it(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.get(
        f"/api/v1/training-units/name/{unit.name}", headers=world.owner_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == unit.name


async def test_get_training_unit_by_name_missing_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/name/nope", headers=world.owner_headers
    )
    assert response.status_code == 404


async def test_get_training_unit_by_name_not_owner_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.get(
        f"/api/v1/training-units/name/{unit.name}", headers=world.other_headers
    )
    assert response.status_code == 404


async def test_get_training_units_by_name_superuser_returns_list(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.get(
        f"/api/v1/training-units/name/{unit.name}/superuser",
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [unit.id]


async def test_get_training_units_by_name_superuser_non_superuser_returns_403(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.get(
        f"/api/v1/training-units/name/{unit.name}/superuser",
        headers=world.other_headers,
    )
    assert response.status_code == 403


async def test_post_training_unit_returns_201(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.post(
        "/api/v1/training-units/",
        json={"name": "brand-new", "description": "d"},
        headers=world.owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "brand-new"


async def test_post_training_unit_duplicate_name_returns_409(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.post(
        "/api/v1/training-units/",
        json={"name": world.owner_units[0].name, "description": "d"},
        headers=world.owner_headers,
    )
    assert response.status_code == 409


async def test_post_training_unit_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/training-units/", json={"name": "x", "description": "d"}
    )
    assert response.status_code == 401


async def test_put_training_unit_owner_returns_200(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.put(
        f"/api/v1/training-units/{unit.id}",
        json={"name": "renamed", "description": "d"},
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "renamed"


async def test_put_training_unit_missing_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.put(
        "/api/v1/training-units/999999",
        json={"name": "x", "description": "d"},
        headers=world.owner_headers,
    )
    assert response.status_code == 404


async def test_put_training_unit_not_owner_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.put(
        f"/api/v1/training-units/{unit.id}",
        json={"name": "x", "description": "d"},
        headers=world.other_headers,
    )
    assert response.status_code == 404


async def test_delete_training_unit_owner_returns_204(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.delete(
        f"/api/v1/training-units/{unit.id}", headers=world.owner_headers
    )
    assert response.status_code == 204


async def test_delete_training_unit_missing_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.delete(
        "/api/v1/training-units/999999", headers=world.owner_headers
    )
    assert response.status_code == 404


async def test_delete_training_unit_not_owner_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.delete(
        f"/api/v1/training-units/{unit.id}", headers=world.other_headers
    )
    assert response.status_code == 404


async def test_add_exercise_to_training_unit_returns_200(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    unit = world.owner_units[0]
    exercise = await create_exercise(db, owner=world.owner)
    response = await client.put(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert [e["id"] for e in response.json()["exercises"]] == [exercise.id]


async def test_added_exercise_output_hides_owner_email(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    # PII regression: the nested exercise payload exposes owner_id, never the
    # owner's email.
    unit = world.owner_units[0]
    exercise = await create_exercise(db, owner=world.owner)
    response = await client.put(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    item = response.json()["exercises"][0]
    assert item["owner_id"] == world.owner.id
    assert "owner" not in item
    assert "email" not in item


async def test_add_exercise_twice_returns_409(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    unit = world.owner_units[0]
    exercise = await create_exercise(db, owner=world.owner)
    await client.put(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    response = await client.put(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 409


async def test_add_exercise_to_missing_unit_returns_404(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    exercise = await create_exercise(db, owner=world.owner)
    response = await client.put(
        f"/api/v1/training-units/999999/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 404


async def test_add_missing_exercise_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.put(
        f"/api/v1/training-units/{unit.id}/exercises/999999",
        headers=world.owner_headers,
    )
    assert response.status_code == 404


async def test_add_exercise_to_not_owned_unit_returns_404(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    unit = world.owner_units[0]
    exercise = await create_exercise(db, owner=world.owner)
    response = await client.put(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.other_headers,
    )
    assert response.status_code == 404


async def test_remove_exercise_from_training_unit_returns_200(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    unit = world.owner_units[0]
    exercise = await create_exercise(db, owner=world.owner)
    await client.put(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    response = await client.delete(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["exercises"] == []


async def test_remove_missing_exercise_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.delete(
        f"/api/v1/training-units/{unit.id}/exercises/999999",
        headers=world.owner_headers,
    )
    assert response.status_code == 404


async def test_remove_exercise_not_in_unit_returns_409(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    # The exercise exists but was never added to the unit -> conflict.
    unit = world.owner_units[0]
    exercise = await create_exercise(db, owner=world.owner)
    response = await client.delete(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 409


async def test_remove_exercise_from_not_owned_unit_returns_404(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    unit = world.owner_units[0]
    exercise = await create_exercise(db, owner=world.owner)
    response = await client.delete(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.other_headers,
    )
    assert response.status_code == 404


async def test_get_exercises_in_unit_owner_returns_empty(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.get(
        f"/api/v1/training-units/{unit.id}/exercises", headers=world.owner_headers
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_get_exercises_in_unit_reflects_added_exercise(
    client: AsyncClient, world: UnitWorld, db: AsyncSession
) -> None:
    unit = world.owner_units[0]
    exercise = await create_exercise(db, owner=world.owner)
    await client.put(
        f"/api/v1/training-units/{unit.id}/exercises/{exercise.id}",
        headers=world.owner_headers,
    )
    response = await client.get(
        f"/api/v1/training-units/{unit.id}/exercises", headers=world.owner_headers
    )
    assert response.status_code == 200
    assert [e["id"] for e in response.json()] == [exercise.id]


async def test_get_exercises_in_missing_unit_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    response = await client.get(
        "/api/v1/training-units/999999/exercises", headers=world.owner_headers
    )
    assert response.status_code == 404


async def test_get_exercises_in_unit_not_owner_returns_404(
    client: AsyncClient, world: UnitWorld
) -> None:
    unit = world.owner_units[0]
    response = await client.get(
        f"/api/v1/training-units/{unit.id}/exercises", headers=world.other_headers
    )
    assert response.status_code == 404
