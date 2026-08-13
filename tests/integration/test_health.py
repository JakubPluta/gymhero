def test_health_is_public(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200 and response.json() == {"status": "ok"}


def test_ready_checks_database(test_client):
    response = test_client.get("/ready")
    assert response.status_code == 200 and response.json() == {"status": "ready"}


def test_request_id_header_present(test_client):
    response = test_client.get("/health")
    headers = {k.lower(): v for k, v in response.headers.items()}
    assert "x-request-id" in headers
