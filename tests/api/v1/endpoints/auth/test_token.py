from httpx import AsyncClient
import pytest
from app.core.auth import decode_access_token, verify_refresh_token


@pytest.mark.auth
async def test_token_with_username(
    client: AsyncClient,
    registered_user: dict,
    user_data: dict
):
    """
    Testing user login with username for token
    """

    login_params = {
        "username": user_data.get("username"),
        "password": user_data.get("password")
    }

    response_token = await client.post("/api/v1/auth/token", data=login_params)
    assert response_token.status_code == 200
    data = response_token.json()

    # Test for JWT
    token_value = data.get("access_token")
    decoded_data = decode_access_token(token_value)
    assert isinstance(decoded_data, dict)
    assert decoded_data.get("sub") == str(registered_user.get("id"))
    assert data.get("token_type") == "bearer"

    # Test for refresh token
    assert "refresh_token" in response_token.cookies
    refresh_token_value = response_token.cookies.get("refresh_token")
    assert refresh_token_value is not None
    decoded_refresh_token = verify_refresh_token(refresh_token_value)
    assert decoded_refresh_token is not None
    assert decoded_refresh_token.get("type") == "refresh"


@pytest.mark.auth
async def test_token_with_email(
    client: AsyncClient,
    registered_user: dict,
    user_data: dict
):
    """
    Testing user login with email as username for token
    """

    login_params = {
        "username": user_data.get("email"),
        "password": user_data.get("password")
    }

    response_token = await client.post("/api/v1/auth/token", data=login_params)
    assert response_token.status_code == 200
    data = response_token.json()

    # Test for JWT
    token_value = data.get("access_token")
    decoded_data = decode_access_token(token_value)
    assert isinstance(decoded_data, dict)
    assert decoded_data.get("sub") == str(registered_user.get("id"))
    assert data.get("token_type") == "bearer"

    # Test for refresh token
    assert "refresh_token" in response_token.cookies
    refresh_token_value = response_token.cookies.get("refresh_token")
    assert refresh_token_value is not None
    decoded_refresh_token = verify_refresh_token(refresh_token_value)
    assert decoded_refresh_token is not None
    assert decoded_refresh_token.get("type") == "refresh"


@pytest.mark.auth
async def test_token_wrong_username(
    client: AsyncClient,
    registered_user: dict,
    user_data: dict
):
    """
    Testing user login with wrong username
    """

    login_params = {
        "username": "not_existing_username",
        "password": user_data.get("password")
    }

    response_token = await client.post("/api/v1/auth/token", data=login_params)
    assert response_token.status_code == 401
    data = response_token.json()
    assert data.get("detail") == "Incorrect email or password"
    assert response_token.headers.get("WWW-Authenticate") == "Bearer"


@pytest.mark.auth
async def test_token_wrong_password(
    client: AsyncClient,
    registered_user: dict,
    user_data: dict
):
    """
    Testing user login with wrong password
    """

    login_params = {
        "username": user_data.get("username"),
        "password": "not_existing_password123!"
    }

    response_token = await client.post("/api/v1/auth/token", data=login_params)
    assert response_token.status_code == 401
    data = response_token.json()
    assert data.get("detail") == "Incorrect email or password"
    assert response_token.headers.get("WWW-Authenticate") == "Bearer"
