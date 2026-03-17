import pytest
from httpx import AsyncClient


@pytest.mark.status
async def test_status(
    client: AsyncClient,
    mocker
):
    """
    Test for health check endpoint.
    Exceptions have their own test in services.
    """
    mock_status = mocker.patch("app.api.v1.endpoints.status.check_vies_health")
    mock_status.return_value = {
        "service": "VIES",
        "status": "operational",
        "latency_ms": 200
    }

    response = await client.get("/api/v1/status")

    assert response.status_code == 200
    data = response.json()

    assert data is not None
    assert data.get("service") == "VIES"
    assert data.get("status") == "operational"
    assert data.get("latency_ms") == 200
