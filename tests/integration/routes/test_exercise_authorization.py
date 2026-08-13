"""Regression tests for the exercise authorization rule.

These cover the two cases broken by the inverted ``or`` in the old
``exercise.py`` (now fixed via the centralized ``authorize_owner_or_superuser``):
a non-superuser editing their *own* exercise, and a superuser editing an
exercise they do *not* own. Both must be allowed.
"""

from gymhero.security import create_access_token
from scripts.core.users import get_or_create_user

_EXERCISE_PAYLOAD = {
    "name": "owners-own-exercise",
    "description": "d",
    "exercise_type_id": 1,
    "level_id": 1,
    "target_body_part_id": 1,
}


def _token(user_id: int) -> str:
    return f"Bearer {create_access_token(str(user_id))}"


def _create_owned_exercise(test_client, token: str, name: str) -> int:
    response = test_client.post(
        "/api/v1/exercises", json={**_EXERCISE_PAYLOAD, "name": name},
        headers={"Authorization": token},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_non_superuser_owner_can_update_and_delete_own_exercise(
    test_client, seed_test_database, get_test_db
):
    owner = get_or_create_user(
        get_test_db, "owner@test.com", "pw", "Owner", False, True
    )
    token = _token(owner.id)
    exercise_id = _create_owned_exercise(test_client, token, "owners-own-exercise")

    update = test_client.put(
        f"/api/v1/exercises/{exercise_id}",
        json={**_EXERCISE_PAYLOAD, "description": "updated"},
        headers={"Authorization": token},
    )
    assert update.status_code == 200

    delete = test_client.delete(
        f"/api/v1/exercises/{exercise_id}", headers={"Authorization": token}
    )
    assert delete.status_code == 204


def test_superuser_can_update_exercise_owned_by_another_user(
    test_client, seed_test_database, get_test_db, valid_jwt_token
):
    owner = get_or_create_user(
        get_test_db, "owner@test.com", "pw", "Owner", False, True
    )
    exercise_id = _create_owned_exercise(
        test_client, _token(owner.id), "someone-elses-exercise"
    )

    # valid_jwt_token belongs to the seeded superuser (id 1), not the owner.
    update = test_client.put(
        f"/api/v1/exercises/{exercise_id}",
        json={**_EXERCISE_PAYLOAD, "name": "someone-elses-exercise",
              "description": "edited-by-admin"},
        headers={"Authorization": valid_jwt_token},
    )
    assert update.status_code == 200


def test_non_owner_non_superuser_is_forbidden(
    test_client, seed_test_database, get_test_db
):
    owner = get_or_create_user(
        get_test_db, "owner@test.com", "pw", "Owner", False, True
    )
    other = get_or_create_user(
        get_test_db, "other@test.com", "pw", "Other", False, True
    )
    exercise_id = _create_owned_exercise(
        test_client, _token(owner.id), "owned-exercise"
    )

    response = test_client.put(
        f"/api/v1/exercises/{exercise_id}",
        json={**_EXERCISE_PAYLOAD, "name": "owned-exercise"},
        headers={"Authorization": _token(other.id)},
    )
    assert (
        response.status_code == 403
        and response.json()["detail"] == "Not enough permissions to update exercise"
    )
