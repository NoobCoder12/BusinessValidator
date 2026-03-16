from httpx import AsyncClient
import pytest


@pytest.mark.business
async def test_get_user_history(
    client: AsyncClient,
    user_with_api_key: str,
    example_validation: dict,
    mocker
):
    """
    Test for getting user history
    """
    # Creating another API call for history test
    mock_api = mocker.patch("app.api.v1.endpoints.business.check_vies_vat")
    mock_api.return_value = {
        'name': '\"NIKE POLAND\" SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ',
        'vat_number': '5272184991',
        'country_code': 'PL',
        'address': 'ul. Koszykowa 61, 00-667 Warszawa',
        'is_valid': True
        }
    headers = {"X-API-KEY": user_with_api_key}
    data = {"tax_id": "5272184991"}
    response = await client.post(
        "/api/v1/business/validate", 
        headers=headers,
        json=data
        )
    assert response.status_code == 200

    # History check
    response = await client.get("/api/v1/business/history", headers=headers)
    assert response.status_code == 200

    # Checking stats
    data = response.json()
    assert isinstance(data, list)

    first_check, second_check = data

    # Test for the first check
    # Function fixture first, desc order
    assert first_check.get('tax_id') == '5272184991'
    assert first_check.get('company_name') == '\"NIKE POLAND\" SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ'
    assert first_check.get('is_vat_active') == True
    assert first_check.get('created_at') is not None

    # Test for the second check
    assert second_check.get('tax_id') == '9111852372'
    assert second_check.get('company_name') == 'FABRYKA MEBLI BODZIO BOGDAN SZEWCZYK SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ'
    assert second_check.get('is_vat_active') == True
    assert second_check.get('created_at') is not None