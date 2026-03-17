import pytest
from app.services.vies_service import check_vies_vat
from zeep.exceptions import TransportError, Fault
import httpx
import app.services.vies_service as vies_module


@pytest.mark.services
async def test_vies_service_TransportError(mocker):
    """
    Testing Transport Error in VIES service API.
    Happy path is tested in endpoints.
    Mocking client not to create external API call.
    """

    # Closing client before test
    vies_module._client = None

    mock_client = mocker.AsyncMock()
    mock_client.service.checkVat.side_effect = TransportError()
    mocker.patch(
        "app.services.vies_service.get_client",
        return_value=mock_client
        )

    result = await check_vies_vat("PL", "1234567899")
    assert result == {"error": "VIES connection error"}


@pytest.mark.services
async def test_vies_service_ConnectionError(mocker):
    """
    Testing Connection Error in VIES service API.
    Happy path is tested in endpoints.
    Mocking client not to create external API call.
    """
    # Closing client before test
    vies_module._client = None

    mock_client = mocker.AsyncMock()
    mock_client.service.checkVat.side_effect = ConnectionError()
    mocker.patch(
        "app.services.vies_service.get_client",
        return_value=mock_client
        )

    result = await check_vies_vat("PL", "1234567899")
    assert result == {"error": "VIES connection error"}


@pytest.mark.services
async def test_vies_service_HTTPError(mocker):
    """
    Testing HTTP Error in VIES service API.
    Happy path is tested in endpoints.
    Mocking client not to create external API call.
    """

    # Closing client before test
    vies_module._client = None

    mock_client = mocker.AsyncMock()
    mock_client.service.checkVat.side_effect = httpx.HTTPError("error")  # Needs a message as arg
    mocker.patch(
        "app.services.vies_service.get_client",
        return_value=mock_client
        )

    result = await check_vies_vat("PL", "1234567899")
    assert result == {"error": "VIES connection error"}


@pytest.mark.services
async def test_vies_service_Fault(mocker):
    """
    Testing Fault for SOAP in VIES service API.
    Happy path is tested in endpoints.
    Mocking client not to create external API call.
    """
    # Closing client before test
    vies_module._client = None

    mock_client = mocker.AsyncMock()
    mock_client.service.checkVat.side_effect = Fault("error")
    mocker.patch(
        "app.services.vies_service.get_client",
        return_value=mock_client
        )

    result = await check_vies_vat("PL", "1234567899")
    assert result == {"error": "Wrong data provided"}


@pytest.mark.services
async def test_vies_service_Exception(mocker):
    """
    Testing Exception in VIES service API.
    Happy path is tested in endpoints.
    Mocking client not to create external API call.
    """
    # Closing client before test
    vies_module._client = None

    mock_client = mocker.AsyncMock()
    mock_client.service.checkVat.side_effect = Exception()
    mocker.patch(
        "app.services.vies_service.get_client",
        return_value=mock_client
        )

    result = await check_vies_vat("PL", "1234567899")
    assert "error" in result
    assert "Error fetching data: " in result.get("error")


@pytest.mark.services
async def test_vies_services_error_client_cleanup(mocker):
    """
    Test for client cleanup during error.
    Must be assigned before function starts
    """
    mock_client = mocker.AsyncMock()

    # Assign client
    vies_module._client = mock_client
    mock_client.service.checkVat.side_effect = TransportError()

    mocker.patch(
        "app.services.vies_service.get_client",
        return_value=mock_client
        )

    result = await check_vies_vat("PL", "1234567899")
    assert "error" in result

    # Check the cleanup
    assert vies_module._client is None
