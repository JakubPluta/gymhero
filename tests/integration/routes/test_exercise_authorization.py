from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.models.exercise import Exercise
from gymhero.models.user import User
from tests.helpers import auth_headers, create_exercise


def _update_payload(exercise: Exercise, **overrides: object) -> dict:
    base = {
        "name": exercise.name,
        "description": "updated",
        "target_body_part_id": exercise.target_body_part_id,
        "level_id": exercise.level_id,
        "exercise_type_id": exercise.exercise_type_id,
    }
    return {**base, **overrides}


async def test_non_superuser_owner_can_update_and_delete_own_exercise(
    client: AsyncClient, regular_user: User, db: AsyncSession
) -> None:
    exercise = await create_exercise(db, owner=regular_user)
    headers = auth_headers(regular_user)

    update = await client.patch(
        f"/api/v1/exercises/{exercise.id}",
        json=_update_payload(exercise),
        headers=headers,
    )
    assert update.status_code == 200

    delete = await client.delete(
        f"/api/v1/exercises/{exercise.id}", headers=headers
    )
    assert delete.status_code == 204


async def test_superuser_can_update_exercise_owned_by_another_user(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    exercise = await create_exercise(db, owner=regular_user)
    update = await client.patch(
        f"/api/v1/exercises/{exercise.id}",
        json=_update_payload(exercise, description="edited-by-admin"),
        headers=superuser_headers,
    )
    assert update.status_code == 200


async def test_non_owner_non_superuser_is_forbidden(
    client: AsyncClient,
    other_user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    exercise = await create_exercise(db, owner=regular_user)
    response = await client.patch(
        f"/api/v1/exercises/{exercise.id}",
        json=_update_payload(exercise),
        headers=other_user_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions to update exercise"
