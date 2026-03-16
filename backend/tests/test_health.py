"""Unit tests for health and readiness endpoints."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import OperationalError

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "OpenCase"
    assert "version" in body


async def test_ready_postgres_ok(client):
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()

    async def override_get_db():
        yield mock_session

    from app.db import get_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.get("/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["services"]["postgres"] == "ok"
    finally:
        app.dependency_overrides.clear()


async def test_ready_postgres_error(client):
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(
        side_effect=OperationalError("conn", {}, Exception())
    )

    async def override_get_db():
        yield mock_session

    from app.db import get_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.get("/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "degraded"
        assert body["services"]["postgres"] == "error"
    finally:
        app.dependency_overrides.clear()
