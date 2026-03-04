from httpx import AsyncClient
import pytest
import uuid


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

    data = dict(response.json())
    user_id = data.get("id")
    assert uuid.UUID(user_id)    # If user_id not UUID - ValueError
    assert data.get("email") == user_data.get("email")
    assert data.get("username") == user_data.get("username")
    assert "password" not in data


@pytest.mark.auth
async def test_register_duplicate_email(
    client: AsyncClient,
    user_data: dict
):
    """
    Testing error for email duplication
    """
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    user_data["username"] = "testing_email"

    response_email_error = await client.post("/api/v1/auth/register", json=user_data)
    assert response_email_error.status_code == 400
    data_email_error = dict(response_email_error.json())
    assert data_email_error.get("detail") == 'Email already registered'


@pytest.mark.auth
async def test_register_duplicate_username(
    client: AsyncClient,
    user_data: dict
):
    """
    Testing error for username duplication
    """
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    user_data["email"] = "test@testing.com"

    response_email_error = await client.post("/api/v1/auth/register", json=user_data)
    assert response_email_error.status_code == 400
    data_email_error = dict(response_email_error.json())
    assert data_email_error.get("detail") == 'Username already taken'
