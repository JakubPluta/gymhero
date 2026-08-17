from dataclasses import dataclass

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.models.training_plan import TrainingPlan
from gymhero.models.user import User
from tests.helpers import (
    create_training_plan,
    create_training_unit,
    create_user,
    page_items,
)


@dataclass(frozen=True)
class PlanWorld:
    owner: User
    owner_headers: dict[str, str]
    other: User
    other_headers: dict[str, str]
    owner_plans: list[TrainingPlan]
    other_plans: list[TrainingPlan]


@pytest.fixture
async def world(
    db: AsyncSession,
    superuser: User,
    superuser_headers: dict[str, str],
    other_user: User,
    other_user_headers: dict[str, str],
) -> PlanWorld:
    # `owner` is a superuser (the /all endpoint is superuser-only); `other` is a
    # regular user, so both the privilege and owner checks get exercised.
    owner_plans = [
        await create_training_plan(db, owner=superuser, name=f"owner-plan-{i}")
        for i in range(5)
    ]
    other_plans = [
        await create_training_plan(db, owner=other_user, name=f"other-plan-{i}")
        for i in range(3)
    ]
    return PlanWorld(
        superuser, superuser_headers, other_user, other_user_headers,
        owner_plans, other_plans,
    )


async def test_get_all_training_plans_superuser_paginates(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/all",
        params={"skip": 0, "limit": 3},
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert len(page_items(response)) == 3


async def test_search_training_plans_on_my_filters_by_name(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/all/my",
        params={"q": "other-plan-2"},
        headers=world.other_headers,
    )
    assert response.status_code == 200
    assert [item["name"] for item in page_items(response)] == ["other-plan-2"]
    assert response.json()["total"] == 1


async def test_search_training_plans_on_my_scopes_to_owner(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/all/my",
        params={"q": "owner-plan"},
        headers=world.other_headers,
    )
    assert page_items(response) == []
    assert response.json()["total"] == 0


async def test_search_training_plans_all_superuser_spans_owners(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/all",
        params={"q": "other-plan"},
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["total"] == len(world.other_plans)


async def test_get_all_training_plans_negative_params_returns_422(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/all",
        params={"skip": -10, "limit": -5},
        headers=world.owner_headers,
    )
    assert response.status_code == 422


async def test_get_all_training_plans_beyond_end_returns_empty(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/all",
        params={"skip": 100, "limit": 1},
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert page_items(response) == []


async def test_get_all_training_plans_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/training-plans/all")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_all_training_plans_non_superuser_returns_403(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/all",
        params={"skip": 0, "limit": 3},
        headers=world.other_headers,
    )
    assert response.status_code == 403


async def test_get_my_training_plans_returns_only_owned(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/all/my",
        params={"limit": 10},
        headers=world.other_headers,
    )
    assert response.status_code == 200
    assert len(page_items(response)) == len(world.other_plans)


async def test_get_my_training_plans_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/training-plans/all/my")
    assert response.status_code == 401


async def test_get_training_plan_by_id_owner_returns_it(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(
        f"/api/v1/training-plans/{plan.id}", headers=world.owner_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == plan.id


async def test_get_training_plan_by_id_missing_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/999999", headers=world.owner_headers
    )
    assert response.status_code == 404


async def test_get_training_plan_by_id_not_owner_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(
        f"/api/v1/training-plans/{plan.id}", headers=world.other_headers
    )
    assert response.status_code == 404


async def test_get_training_plan_by_name_owner_returns_it(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(
        f"/api/v1/training-plans/name/{plan.name}", headers=world.owner_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == plan.name


async def test_get_training_plan_by_name_missing_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/name/nope", headers=world.owner_headers
    )
    assert response.status_code == 404


async def test_get_training_plan_by_name_not_owner_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(
        f"/api/v1/training-plans/name/{plan.name}", headers=world.other_headers
    )
    assert response.status_code == 404


async def test_get_training_plan_by_name_anonymous_returns_401(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(f"/api/v1/training-plans/name/{plan.name}")
    assert response.status_code == 401


async def test_get_training_plans_by_name_superuser_returns_list(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(
        f"/api/v1/training-plans/name/{plan.name}/superuser",
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [plan.id]


async def test_get_training_plans_by_name_superuser_missing_returns_empty(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/name/nope/superuser", headers=world.owner_headers
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_get_training_plans_by_name_superuser_non_superuser_returns_403(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(
        f"/api/v1/training-plans/name/{plan.name}/superuser",
        headers=world.other_headers,
    )
    assert response.status_code == 403


async def test_post_training_plan_returns_201(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.post(
        "/api/v1/training-plans",
        json={"name": "brand-new", "description": "d"},
        headers=world.owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "brand-new"


async def test_post_training_plan_duplicate_name_for_owner_returns_409(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.post(
        "/api/v1/training-plans",
        json={"name": world.owner_plans[0].name, "description": "d"},
        headers=world.owner_headers,
    )
    assert response.status_code == 409


async def test_post_training_plan_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/training-plans", json={"name": "x", "description": "d"}
    )
    assert response.status_code == 401


async def test_put_training_plan_owner_returns_200(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.put(
        f"/api/v1/training-plans/{plan.id}",
        json={"name": "renamed", "description": "d"},
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "renamed"


async def test_put_training_plan_missing_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.put(
        "/api/v1/training-plans/999999",
        json={"name": "x", "description": "d"},
        headers=world.owner_headers,
    )
    assert response.status_code == 404


async def test_put_training_plan_not_owner_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.put(
        f"/api/v1/training-plans/{plan.id}",
        json={"name": "x", "description": "d"},
        headers=world.other_headers,
    )
    assert response.status_code == 404


async def test_delete_training_plan_owner_returns_204(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.delete(
        f"/api/v1/training-plans/{plan.id}", headers=world.owner_headers
    )
    assert response.status_code == 204


async def test_delete_training_plan_missing_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.delete(
        "/api/v1/training-plans/999999", headers=world.owner_headers
    )
    assert response.status_code == 404


async def test_delete_training_plan_not_owner_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.delete(
        f"/api/v1/training-plans/{plan.id}", headers=world.other_headers
    )
    assert response.status_code == 404


async def test_add_training_unit_to_plan_returns_200(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    plan = world.owner_plans[0]
    unit = await create_training_unit(db, owner=world.owner)
    response = await client.put(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == plan.id
    assert [tu["id"] for tu in body["training_units"]] == [unit.id]


async def test_add_training_unit_twice_returns_409(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    plan = world.owner_plans[0]
    unit = await create_training_unit(db, owner=world.owner)
    await client.put(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.owner_headers,
    )
    response = await client.put(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 409


async def test_add_missing_training_unit_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.put(
        f"/api/v1/training-plans/{plan.id}/training-units/999999",
        headers=world.owner_headers,
    )
    assert response.status_code == 404


async def test_add_training_unit_to_missing_plan_returns_404(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    unit = await create_training_unit(db, owner=world.owner)
    response = await client.put(
        f"/api/v1/training-plans/999999/training-units/{unit.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 404


async def test_add_training_unit_to_not_owned_plan_returns_404(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    plan = world.owner_plans[0]
    unit = await create_training_unit(db, owner=world.other)
    response = await client.put(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.other_headers,
    )
    assert response.status_code == 404


async def test_regular_user_cannot_attach_another_users_unit_to_own_plan(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    # F1 (object-level authz): a plan owner must not attach — and thereby read via
    # the plan — a unit owned by someone else. Non-owner => 404, like a direct GET.
    attacker_plan = await create_training_plan(db, owner=world.other)
    victim = await create_user(db)
    victim_unit = await create_training_unit(db, owner=victim)

    response = await client.put(
        f"/api/v1/training-plans/{attacker_plan.id}/training-units/{victim_unit.id}",
        headers=world.other_headers,
    )
    assert response.status_code == 404


async def test_remove_missing_training_unit_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.delete(
        f"/api/v1/training-plans/{plan.id}/training-units/999999",
        headers=world.owner_headers,
    )
    assert response.status_code == 404


async def test_remove_training_unit_not_in_plan_returns_409(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    # The unit exists but was never added to the plan -> conflict, not "missing".
    plan = world.owner_plans[0]
    unit = await create_training_unit(db, owner=world.owner)
    response = await client.delete(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 409


async def test_remove_training_unit_returns_200(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    plan = world.owner_plans[0]
    unit = await create_training_unit(db, owner=world.owner)
    await client.put(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.owner_headers,
    )
    response = await client.delete(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.owner_headers,
    )
    assert response.status_code == 200


async def test_remove_training_unit_not_owned_plan_returns_404(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    plan = world.owner_plans[0]
    unit = await create_training_unit(db, owner=world.owner)
    response = await client.delete(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.other_headers,
    )
    assert response.status_code == 404


async def test_get_training_units_in_plan_owner_returns_empty(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(
        f"/api/v1/training-plans/{plan.id}/training-units",
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_get_training_units_in_plan_reflects_added_unit(
    client: AsyncClient, world: PlanWorld, db: AsyncSession
) -> None:
    plan = world.owner_plans[0]
    unit = await create_training_unit(db, owner=world.owner)
    await client.put(
        f"/api/v1/training-plans/{plan.id}/training-units/{unit.id}",
        headers=world.owner_headers,
    )
    response = await client.get(
        f"/api/v1/training-plans/{plan.id}/training-units",
        headers=world.owner_headers,
    )
    assert response.status_code == 200
    assert [tu["id"] for tu in response.json()] == [unit.id]


async def test_get_training_units_in_plan_not_owner_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    plan = world.owner_plans[0]
    response = await client.get(
        f"/api/v1/training-plans/{plan.id}/training-units",
        headers=world.other_headers,
    )
    assert response.status_code == 404


async def test_get_training_units_in_missing_plan_returns_404(
    client: AsyncClient, world: PlanWorld
) -> None:
    response = await client.get(
        "/api/v1/training-plans/999999/training-units", headers=world.owner_headers
    )
    assert response.status_code == 404
