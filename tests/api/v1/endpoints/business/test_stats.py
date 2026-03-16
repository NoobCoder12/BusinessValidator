from httpx import AsyncClient
import pytest


@pytest.mark.business
async def test_get_user_stats(
    client: AsyncClient,
    user_with_api_key: str,
    example_validation: dict
):
    """
    Test for getting user statistics of business checks
    """

    headers = {"X-API-KEY": user_with_api_key}

    response = await client.get("/api/v1/business/stats/me", headers=headers)
    assert response.status_code == 200

    # Checking stats
    data = response.json()
    assert data.get("total_searches") == 1
    assert data.get("active_vat_pct") == "100.00%"
    assert data.get("last_activity") is not None

    # Most searched details
    most_searched_data = data.get("most_searched")
    assert most_searched_data.get("tax_id") == "9111852372"
    assert most_searched_data.get("count") == 1
