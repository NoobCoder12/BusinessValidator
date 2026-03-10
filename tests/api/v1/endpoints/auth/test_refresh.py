from httpx import AsyncClient
import pytest
from app.core.auth import decode_access_token
from datetime import datetime, timezone, timedelta
from jose import jwt
from app.core.config import settings
import uuid


@pytest.mark.auth
async def test_refresh(
    client: AsyncClient,
    logged_user: dict,      # get headers as logged user
    registered_user: dict
):
    response = await client.post("/api/v1/auth/refresh", headers=logged_user)
    assert response.status_code == 200
    data = response.json()
    token = data.get("access_token")

    assert isinstance(token, str)

    decoded_data = dict(decode_access_token(token))

    assert isinstance(decoded_data, dict)
    assert decoded_data.get("sub") == str(registered_user.get("id"))
    assert data.get("token_type") == "bearer"
    assert decoded_data.get("type") == "access"

    exp = decoded_data.get("exp")
    assert exp is not None
    assert datetime.fromtimestamp(exp, tz=timezone.utc) > datetime.now(tz=timezone.utc)


@pytest.mark.auth
async def test_refresh_empty(
    client: AsyncClient,
    registered_user: dict
):
    """
    Test for endpoint with no refresh token
    """
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "No refresh token found"


@pytest.mark.auth
async def test_refresh_expired(
    client: AsyncClient,
    user_data: dict
):
    """
    Test for endpoint with expired refresh token
    """
    # Create user for this test
    response_user = await client.post("/api/v1/auth/register", json=user_data)
    assert response_user.status_code == 201
    data = response_user.json()

    # Create refresh token with expired date
    expired_payload = {
        "sub": str(data.get("id")),
        "exp": 1000000000,      # year 2001 - expired
        "type": "refresh"
    }

    expired_refresh_token = jwt.encode(
        expired_payload,
        settings.REFRESH_TOKEN_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    # Set new cookie with expired refresh token
    client.cookies.set("refresh_token", expired_refresh_token)

    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Token expired or is not valid"


@pytest.mark.auth
async def test_refresh_no_user(
    client: AsyncClient
):
    # Create refresh token with non-existing user
    expired_payload = {
        "sub": str(uuid.UUID("550e8400-e29b-41d4-a716-446655440000")),   # random ID
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
        "type": "refresh"
    }

    refresh_token = jwt.encode(
        expired_payload,
        settings.REFRESH_TOKEN_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    # Set new cookie with non-existing user
    client.cookies.set("refresh_token", refresh_token)

    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "User does not exist"
