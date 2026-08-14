from httpx import AsyncClient


async def test_health_is_public(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_checks_database(client: AsyncClient) -> None:
    response = await client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


async def test_request_id_header_present(client: AsyncClient) -> None:
    response = await client.get("/health")
    headers = {key.lower(): value for key, value in response.headers.items()}
    assert "x-request-id" in headers
