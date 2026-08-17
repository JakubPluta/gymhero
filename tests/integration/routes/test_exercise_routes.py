from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.models.user import User
from tests.helpers import (
    create_body_part,
    create_exercise,
    create_exercise_type,
    create_level,
    page_items,
)


def _payload(*, name: str, body_part_id: int, level_id: int, type_id: int) -> dict:
    return {
        "name": name,
        "description": "d",
        "target_body_part_id": body_part_id,
        "level_id": level_id,
        "exercise_type_id": type_id,
    }


async def test_get_exercises_anonymous_returns_401(client: AsyncClient) -> None:
    # H1: exercise reads now require authentication.
    response = await client.get("/api/v1/exercises/all")
    assert response.status_code == 401


async def test_get_exercises_authenticated_returns_items(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    await create_exercise(db, owner=regular_user)
    response = await client.get("/api/v1/exercises/all", headers=user_headers)
    assert response.status_code == 200
    assert len(page_items(response)) == 1


async def test_get_exercises_respects_limit(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    await create_exercise(db, owner=regular_user)
    await create_exercise(db, owner=regular_user)
    response = await client.get(
        "/api/v1/exercises/all", params={"limit": 1}, headers=user_headers
    )
    assert response.status_code == 200
    assert len(page_items(response)) == 1


async def test_get_my_exercises_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/exercises/my")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_my_exercises_returns_only_owned(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    other_user: User,
    db: AsyncSession,
) -> None:
    mine = await create_exercise(db, owner=regular_user)
    await create_exercise(db, owner=other_user)
    response = await client.get("/api/v1/exercises/my", headers=user_headers)
    assert response.status_code == 200
    assert [item["id"] for item in page_items(response)] == [mine.id]


async def test_search_exercises_by_name_is_partial_and_case_insensitive(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    await create_exercise(db, owner=regular_user, name="Barbell Bench Press")
    await create_exercise(db, owner=regular_user, name="Back Squat")
    response = await client.get(
        "/api/v1/exercises/all", params={"q": "bench"}, headers=user_headers
    )
    assert response.status_code == 200
    assert [item["name"] for item in page_items(response)] == ["Barbell Bench Press"]
    assert response.json()["total"] == 1


async def test_filter_exercises_by_type(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    strength = await create_exercise_type(db)
    cardio = await create_exercise_type(db)
    await create_exercise(db, owner=regular_user, exercise_type=strength)
    await create_exercise(db, owner=regular_user, exercise_type=cardio)
    response = await client.get(
        "/api/v1/exercises/all",
        params={"exercise_type_id": strength.id},
        headers=user_headers,
    )
    assert response.status_code == 200
    items = page_items(response)
    assert len(items) == 1
    assert items[0]["exercise_type"]["id"] == strength.id
    assert response.json()["total"] == 1


async def test_search_query_and_filter_combine(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    strength = await create_exercise_type(db)
    cardio = await create_exercise_type(db)
    await create_exercise(
        db, owner=regular_user, name="Bench Press", exercise_type=strength
    )
    await create_exercise(
        db, owner=regular_user, name="Bench Cardio", exercise_type=cardio
    )
    await create_exercise(db, owner=regular_user, name="Squat", exercise_type=strength)
    response = await client.get(
        "/api/v1/exercises/all",
        params={"q": "bench", "exercise_type_id": strength.id},
        headers=user_headers,
    )
    assert [item["name"] for item in page_items(response)] == ["Bench Press"]
    assert response.json()["total"] == 1


async def test_search_total_reflects_filter_not_page(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    for index in range(3):
        await create_exercise(db, owner=regular_user, name=f"Bench {index}")
    await create_exercise(db, owner=regular_user, name="Squat")
    response = await client.get(
        "/api/v1/exercises/all",
        params={"q": "bench", "limit": 2},
        headers=user_headers,
    )
    assert len(page_items(response)) == 2  # page capped by limit
    assert response.json()["total"] == 3  # total reflects all matches


async def test_search_on_my_scopes_to_owner(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    other_user: User,
    db: AsyncSession,
) -> None:
    await create_exercise(db, owner=regular_user, name="Bench Mine")
    await create_exercise(db, owner=other_user, name="Bench Theirs")
    response = await client.get(
        "/api/v1/exercises/my", params={"q": "bench"}, headers=user_headers
    )
    assert [item["name"] for item in page_items(response)] == ["Bench Mine"]


async def test_get_exercise_by_id_returns_it(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    exercise = await create_exercise(db, owner=regular_user)
    response = await client.get(
        f"/api/v1/exercises/{exercise.id}", headers=user_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == exercise.id


async def test_get_exercise_embeds_lookup_objects_not_ids(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    # Read contract: lookups embedded as nested {id, name}; raw FK ids live only on
    # the write schema; owner stays a bare id (never the User row / PII).
    body_part = await create_body_part(db)
    level = await create_level(db)
    exercise_type = await create_exercise_type(db)
    exercise = await create_exercise(
        db,
        owner=regular_user,
        body_part=body_part,
        level=level,
        exercise_type=exercise_type,
    )

    response = await client.get(
        f"/api/v1/exercises/{exercise.id}", headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()

    assert data["exercise_type"] == {"id": exercise_type.id, "name": exercise_type.name}
    assert data["level"] == {"id": level.id, "name": level.name}
    assert data["target_body_part"] == {"id": body_part.id, "name": body_part.name}

    assert data["owner_id"] == regular_user.id
    assert "exercise_type_id" not in data
    assert "level_id" not in data
    assert "target_body_part_id" not in data


async def test_get_exercise_by_id_missing_returns_404(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/exercises/999999", headers=user_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise with id 999999 not found"


async def test_get_exercise_by_name_returns_it(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    await create_exercise(db, owner=regular_user, name="Bench Press")
    response = await client.get(
        "/api/v1/exercises/name/Bench Press", headers=user_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Bench Press"


async def test_get_exercise_by_name_missing_returns_404(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/exercises/name/abc", headers=user_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise with name abc not found"


async def test_post_exercise_returns_201(
    client: AsyncClient, user_headers: dict[str, str], db: AsyncSession
) -> None:
    body_part = await create_body_part(db)
    level = await create_level(db)
    exercise_type = await create_exercise_type(db)
    response = await client.post(
        "/api/v1/exercises",
        json=_payload(
            name="Squat",
            body_part_id=body_part.id,
            level_id=level.id,
            type_id=exercise_type.id,
        ),
        headers=user_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Squat"


async def test_post_exercise_duplicate_name_returns_409(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    existing = await create_exercise(db, owner=regular_user, name="Squat")
    response = await client.post(
        "/api/v1/exercises",
        json=_payload(
            name="Squat",
            body_part_id=existing.target_body_part_id,
            level_id=existing.level_id,
            type_id=existing.exercise_type_id,
        ),
        headers=user_headers,
    )
    assert response.status_code == 409


async def test_post_exercise_anonymous_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/exercises", json={"name": "Squat", "description": "d"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_patch_exercise_owner_returns_200(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    exercise = await create_exercise(db, owner=regular_user)
    response = await client.patch(
        f"/api/v1/exercises/{exercise.id}",
        json=_payload(
            name="Updated",
            body_part_id=exercise.target_body_part_id,
            level_id=exercise.level_id,
            type_id=exercise.exercise_type_id,
        ),
        headers=user_headers,
    )
    assert response.status_code == 200


async def test_patch_exercise_missing_returns_404(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.patch(
        "/api/v1/exercises/999999",
        json=_payload(name="Updated", body_part_id=1, level_id=1, type_id=1),
        headers=user_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise with id 999999 not found"


async def test_patch_exercise_not_owner_returns_403(
    client: AsyncClient,
    other_user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    exercise = await create_exercise(db, owner=regular_user)
    response = await client.patch(
        f"/api/v1/exercises/{exercise.id}",
        json=_payload(
            name="Updated",
            body_part_id=exercise.target_body_part_id,
            level_id=exercise.level_id,
            type_id=exercise.exercise_type_id,
        ),
        headers=other_user_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions to update exercise"


async def test_delete_exercise_owner_returns_204(
    client: AsyncClient,
    user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    exercise = await create_exercise(db, owner=regular_user)
    response = await client.delete(
        f"/api/v1/exercises/{exercise.id}", headers=user_headers
    )
    assert response.status_code == 204


async def test_delete_exercise_missing_returns_404(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.delete("/api/v1/exercises/10000", headers=user_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise with id 10000 not found. Cannot delete."


async def test_delete_exercise_not_owner_returns_403(
    client: AsyncClient,
    other_user_headers: dict[str, str],
    regular_user: User,
    db: AsyncSession,
) -> None:
    exercise = await create_exercise(db, owner=regular_user)
    response = await client.delete(
        f"/api/v1/exercises/{exercise.id}", headers=other_user_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions to delete exercise"
