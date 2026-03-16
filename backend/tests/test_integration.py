import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.mark.integration
async def test_health_endpoint_live() -> None:
    """Hit the running server to verify the health endpoint."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "OpenCase"


@pytest.mark.integration
async def test_ready_endpoint_postgres_ok() -> None:
    """Readiness probe reports postgres=ok when the compose stack is running."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["services"]["postgres"] == "ok"
