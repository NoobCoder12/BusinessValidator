from zeep import AsyncClient
from zeep.helpers import serialize_object
from zeep.exceptions import TransportError, Fault
from zeep.transports import AsyncTransport
import httpx    #

# TODO: think about async if there is more requests

WSDL = "https://ec.europa.eu/taxation_customs/vies/services/checkVatService.wsdl"

_client = None


async def get_client():
    """
    Function created to re-initialize client in case of
    his error when zeep can't handle it alone.
    If client is None it gets created
    """
    global _client
    if _client is None:
        # Creating Transport to set timeout for fetching data
        engine = httpx.AsyncClient(timeout=10)
        client_transport = AsyncTransport(client=engine)     # Zeep needs AsyncTransport by default to work with AsyncClient
        _client = AsyncClient(wsdl=WSDL, transport=client_transport)
    return _client


async def check_vies_vat(country: str, nip: str):
    """
    Sends a SOAP request to VIES to validate a VAT number.
    Returns a dictionary with the company name or an error message.
    """
    global _client

    try:
        client = await get_client()

        result = await client.service.checkVat(countryCode=country, vatNumber=nip)

        # Changing into dict
        result_dict = serialize_object(result)

        # Using .get() to prevent an error in case of missing data
        clean_data = {
            "name": result_dict.get("name"),
            "vat_number": result_dict.get("vatNumber"),
            "country_code": result_dict.get("countryCode"),
            "address": result_dict.get("address"),
            "is_valid": result_dict.get("valid"),
        }

        return clean_data

    except (TransportError, ConnectionError, httpx.HTTPError):
        if _client:
            # httpx needs to be unpacked from Zeep
            await _client.transport.client.aclose()    # Closing socket, killing zombie connections
        # Clearing out client to initialize it again
        _client = None
        return {"error": "VIES connection error"}

    # When SOAP doesn't understand provided data
    except Fault:
        return {"error": "Wrong data provided"}

    except Exception as e:
        return {"error": f"Error fetching data: {e}"}
