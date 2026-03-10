from httpx import AsyncClient
import pytest


@pytest.mark.auth
async def test_api_key(
    client: AsyncClient,
    logged_user: dict
):
    """
    Test for getting api key
    """
    response = await client.post("/api/v1/auth/me/api-key", headers=logged_user)
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    key = data.get("api_key")
    assert isinstance(key, str)


@pytest.mark.auth
async def test_api_key_unauthorized(
    client: AsyncClient
):
    """
    Test for getting api key as non logged user
    """
    response = await client.post("/api/v1/auth/me/api-key")
    assert response.status_code == 401
