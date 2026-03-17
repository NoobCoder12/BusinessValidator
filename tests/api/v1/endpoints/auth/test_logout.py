from httpx import AsyncClient
import pytest


@pytest.mark.auth
async def test_logout(
    client: AsyncClient,
    logged_user: dict,
    registered_user: dict,
    user_data: dict
):
    """
    Test for logout endpoint
    """
    login_params = {
        "username": user_data.get("username"),
        "password": user_data.get("password")
    }

    # Creating refresh token
    response = await client.post("/api/v1/auth/token", data=login_params)
    assert response.status_code == 200
    assert response.cookies.get("refresh_token") is not None

    # Deleting refresh token
    response_logout = await client.post("/api/v1/auth/logout", headers=logged_user)
    assert response_logout.status_code == 200
    cookie = response_logout.cookies.get("refresh_token")
    assert cookie is None or cookie == ""   # may leave empty string

    # Testing if deleted
    response_deleted = await client.post("/api/v1/auth/refresh", headers=logged_user)
    assert response_deleted.status_code == 401