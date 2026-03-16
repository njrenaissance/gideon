from pathlib import Path

from dotenv import load_dotenv

# Load test environment before any app imports.
# Required fields (OPENCASE_AUTH_SECRET_KEY, OPENCASE_DB_URL) must be set
# before config.py is imported, because Settings() is instantiated at module level.
load_dotenv(Path(__file__).parent.parent / ".env.test")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
