from httpx import AsyncClient
import pytest
import uuid
import json


@pytest.mark.business
async def test_validate_business_real(
    client: AsyncClient,
    user_with_api_key: str,
):
    """
    Test for one real request - Smoke Test
    """
    headers = {
        "X-API-KEY": user_with_api_key
    }

    data = {
        "tax_id": "5252530705"  # Example tax ID
    }

    response = await client.post(
        "/api/v1/business/validate", 
        headers=headers,
        json=data
        )

    assert response.status_code == 200

    business_data = response.json()
    assert business_data is not None

    # Business check ID
    busiess_check_id = business_data.get("id")
    assert str(uuid.UUID(busiess_check_id))

    # Company name
    company_name = business_data.get("company_name")
    assert company_name == "FACEBOOK POLAND SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ" or isinstance(company_name, str) # In case of name change

    # Is it an active VAT taxpayer
    assert isinstance(business_data.get("is_vat_active"), bool)

    # Is date of business check empty
    date = business_data.get("created_at")
    assert isinstance(date, str) and date is not None


@pytest.mark.business
async def test_validate_business_mock(
    client: AsyncClient,
    user_with_api_key: str,
    mocker  # Fixture by default
):
    """
    Test for business validation endpoint with mocked data.
    Assertions are made using data returned by endpoint.
    """
    # Creating mock for API request
    # Path to location where service is used + name of service function
    mock_api = mocker.patch("app.api.v1.endpoints.business.check_vies_vat")

    # Assigning value to return
    # Must be the same data that service returns
    mock_api.return_value = {
        'name': 'FACEBOOK POLAND SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ',
        'vat_number': '5252530705',
        'country_code': 'PL',
        'address': 'ul. Koszykowa 61, 00-667 Warszawa',
        'is_valid': True
        }

    headers = {
        "X-API-KEY": user_with_api_key
    }

    data = {
        "tax_id": "5252530705"  # Example tax ID
    }

    response = await client.post(
        "/api/v1/business/validate", 
        headers=headers,
        json=data
        )

    assert response.status_code == 200

    business_data = response.json()
    print(f"MOJA DATA: {business_data}")
    assert business_data is not None

    # Business check ID
    busiess_check_id = business_data.get("id")
    assert str(uuid.UUID(busiess_check_id))

    # Company name
    company_name = business_data.get("company_name")
    assert company_name == "FACEBOOK POLAND SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ" or isinstance(company_name, str) # In case of name change

    # Is it an active VAT taxpayer
    assert isinstance(business_data.get("is_vat_active"), bool)

    # Is date of business check empty
    date = business_data.get("created_at")
    assert isinstance(date, str) and date is not None


@pytest.mark.business
async def test_validate_business_check_db(
    client: AsyncClient,
    user_with_api_key: str,
    mocker  # Fixture by default
):
    """
    Test for checking for a result in database.
    Assertions are made using data returned by endpoint.
    """

    # Creating mock for API request
    # Path to location where service is used + name of service function
    mock_api = mocker.patch("app.api.v1.endpoints.business.check_vies_vat")

    # Assigning value to return
    # Must be the same data that service returns
    mock_api.return_value = {
        'name': 'FACEBOOK POLAND SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ',
        'vat_number': '5252530705',
        'country_code': 'PL',
        'address': 'ul. Koszykowa 61, 00-667 Warszawa',
        'is_valid': True
        }

    # Creating request first
    headers = {"X-API-KEY": user_with_api_key}
    data = {"tax_id": "5252530705"}  # Example tax ID
    response = await client.post(
        "/api/v1/business/validate",
        headers=headers,
        json=data
        )
    assert response.status_code == 200
    assert mock_api.call_count == 1

    # Calling the same tax ID
    response_database = await client.post(
        "/api/v1/business/validate", 
        headers=headers,
        json=data
        )

    # Checking if another API call was made
    assert response_database.status_code == 200
    assert mock_api.call_count == 1


@pytest.mark.business
async def test_validate_business_check_redis(
    client: AsyncClient,
    user_with_api_key: str,
    redis_client,   # fixture created in conftest
    mocker
):
    """
    Test for redis caching
    """

    # Preparing redis element for test
    nip = "5252530705"
    cache_key = f"bus:v1:{nip}"
    data = {
        'name': 'FACEBOOK POLAND SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ', 
        'vat_number': '5252530705',
        'is_valid': True,
        }

    await redis_client.set(cache_key, json.dumps(data))

    # Creating mock for API request
    # Path to location where service is used + name of service function
    mock_api = mocker.patch("app.api.v1.endpoints.business.check_vies_vat")

    # Assigning value to return
    # Must be the same data that service returns
    mock_api.return_value = {
        'name': 'FACEBOOK POLAND SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ',
        'vat_number': '5252530705',
        'country_code': 'PL',
        'address': 'ul. Koszykowa 61, 00-667 Warszawa',
        'is_valid': True
        }

    # Creating request to endpoint
    headers = {"X-API-KEY": user_with_api_key}
    response = await client.post(
        "/api/v1/business/validate",
        headers=headers,
        json={"tax_id": f"{nip}"}
        )

    assert response.status_code == 200
    assert mock_api.call_count == 0
