from httpx import AsyncClient
import pytest


@pytest.mark.auth
async def test_me(
    client: AsyncClient,
    logged_user: dict,      # get headers as logged user
    registered_user: dict
):
    """
    Test for getting logged user data
    """

    response = await client.get("/api/v1/auth/me", headers=logged_user)

    assert response.status_code == 200
    data = response.json()

    assert data.get("id") == str(registered_user.get("id"))
    assert data.get("email") == registered_user.get("email")
    assert data.get("username") == registered_user.get("username")
