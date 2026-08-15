from httpx import AsyncClient
from pytest_mock import MockerFixture


async def test_cors_preflight_allowed(client: AsyncClient) -> None:
    response = await client.options(
        "/api/v1/levels/all",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"


async def test_request_id_is_echoed(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Request-ID": "trace-abc"})
    assert response.headers["x-request-id"] == "trace-abc"


async def test_unhandled_error_returns_clean_500_with_request_id(
    client: AsyncClient, mocker: MockerFixture
) -> None:
    # A raw (non-domain, non-DB) error must map to a generic 500 that still
    # carries the request id and never leaks internals.
    mocker.patch(
        "gymhero.crud.base.CRUDRepository.get_many", side_effect=ValueError("boom")
    )
    response = await client.get(
        "/api/v1/levels/all", headers={"X-Request-ID": "trace-500"}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert response.headers["x-request-id"] == "trace-500"
