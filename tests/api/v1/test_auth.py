from httpx import AsyncClient
import pytest


@pytest.mark.auth
async def test_register_user(
    client: AsyncClient,
    user_data: dict
):
    """
    Testing user registration
    """
    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
