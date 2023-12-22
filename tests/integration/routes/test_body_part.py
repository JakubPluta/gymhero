def test_get_all_body_parts(
    test_client, seed_body_parts, valid_jwt_token, first_active_superuser
):
    response = test_client.get(
        "/body-parts/all",
        params={"limit": 3, "skip": 0},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    response = test_client.get("/body-parts/all", params={"limit": 1, "skip": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_one_body_part(
    test_client, seed_body_parts, valid_jwt_token, first_active_superuser
):
    response = test_client.get(
        "/body-parts/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

    response = test_client.get(
        "/body-parts/name/Biceps", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Biceps"

    response = test_client.get(
        "/body-parts/100", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Body part with id 100 not found"

    response = test_client.get(
        "/body-parts/name/abc", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Body part with name abc not found"


def test_can_create_body_part(test_client, valid_jwt_token, first_active_superuser):
    response = test_client.post(
        "/body-parts",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 201

    response = test_client.post(
        "/body-parts",
        json={"name": "test", "description": "test"},
    )
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )

    response = test_client.post(
        "/body-parts",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 409
        and response.json()["detail"] == "Body part with name test already exists"
    )


def test_can_delete_body_part(
    test_client, seed_body_parts, valid_jwt_token, first_active_superuser
):
    response = test_client.delete(
        "/body-parts/1", headers={"Authorization": valid_jwt_token}
    )
    assert response.status_code == 200

    response = test_client.delete(
        "/body-parts/100", headers={"Authorization": valid_jwt_token}
    )
    assert (
        response.status_code == 404
        and response.json()["detail"]
        == "Body part with id 100 not found. Cannot delete."
    )

    response = test_client.delete("/body-parts/1")
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )


def test_can_update_body_part(
    test_client, seed_body_parts, valid_jwt_token, first_active_superuser
):
    response = test_client.put(
        "/body-parts/1",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert response.status_code == 200 and response.json()["name"] == "test"

    response = test_client.put(
        "/body-parts/100",
        json={"name": "test", "description": "test"},
        headers={"Authorization": valid_jwt_token},
    )
    assert (
        response.status_code == 404
        and response.json()["detail"]
        == "Body part with id 100 not found. Cannot update."
    )

    response = test_client.put(
        "/body-parts/1",
        json={"name": "test", "description": "test"},
    )
    assert (
        response.status_code == 401 and response.json()["detail"] == "Not authenticated"
    )
