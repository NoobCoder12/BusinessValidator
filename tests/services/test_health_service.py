import pytest
from app.services.health_service import check_vies_health


@pytest.mark.services
async def test_health_service(mocker):
    """
    Test for health service
    """

    # Async because basic funcion uses AsyncClient
    mock_client = mocker.AsyncMock()

    # async with AsyncClient() as client → __aenter__.return_value to "client"
    # await client.get() → .get.return_value to "response"
    # response.status_code → .status_code = 200
    mock_client.__aenter__.return_value.get.return_value.status_code = 200

    mocker.patch(
        "app.services.health_service.httpx.AsyncClient",
        return_value=mock_client
        )

    result = await check_vies_health()
    assert result["status"] == "operational"
    assert result["service"] == "VIES"
    assert isinstance(result["latency_ms"], int)


@pytest.mark.services
async def test_health_service_wrong_status(mocker):
    """
    Test for health service with wrong status code.
    """

    # Async because basic funcion uses AsyncClient
    mock_client = mocker.AsyncMock()

    # async with AsyncClient() as client → __aenter__.return_value to "client"
    # await client.get() → .get.return_value to "response"
    # response.status_code → .status_code = 200
    mock_client.__aenter__.return_value.get.return_value.status_code = 404

    mocker.patch(
        "app.services.health_service.httpx.AsyncClient",
        return_value=mock_client
        )

    result = await check_vies_health()
    assert result["status"] == "degraded"
    assert result["service"] == "VIES"
    assert isinstance(result["latency_ms"], int)


@pytest.mark.services
async def test_health_service_exception(mocker):
    """
    Test for health service with Exception.
    """

    # Async because basic funcion uses AsyncClient
    mock_client = mocker.AsyncMock()

    # async with AsyncClient() as client → __aenter__.return_value to "client"
    mock_client.__aenter__.return_value.get.side_effect = Exception()

    mocker.patch(
        "app.services.health_service.httpx.AsyncClient",
        return_value=mock_client
        )

    result = await check_vies_health()
    assert result["status"] == "down"
    assert result["service"] == "VIES"
    assert result["latency_ms"] is None
