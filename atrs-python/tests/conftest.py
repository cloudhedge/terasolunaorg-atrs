"""Pytest configuration and fixtures."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Note: These imports will work after installing dependencies
# from atrs.main import app
# from atrs.config.settings import settings


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for async tests."""
    return "asyncio"


# Uncomment after installing dependencies and setting up test database
# @pytest_asyncio.fixture
# async def client():
#     """Async test client for API tests."""
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://test"
#     ) as ac:
#         yield ac


# @pytest_asyncio.fixture
# async def auth_token(client: AsyncClient) -> str:
#     """Get authentication token for protected endpoints."""
#     response = await client.post(
#         "/api/v1/auth/login",
#         data={
#             "username": "0000000001",  # Test member
#             "password": "password",
#         }
#     )
#     return response.json()["access_token"]
