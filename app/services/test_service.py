import httpx
from zeep import Client
from zeep.helpers import serialize_object
# Function for sending raw XML file
# def send_request(country: str, nip: str):
#     URL = "http://ec.europa.eu/taxation_customs/vies/services/checkVatService"
#     body = f"""
#     <?xml version="1.0" encoding="utf-8"?>
#     <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
#     <soap:Body>
#         <tns1:checkVat xmlns:tns1="urn:ec.europa.eu:taxud:vies:services:checkVat:types">
#         <tns1:countryCode>{country}</tns1:countryCode>
#         <tns1:vatNumber>{nip}</tns1:vatNumber>
#         </tns1:checkVat>
#     </soap:Body>
#     </soap:Envelope>
#     """.strip()
#     headers = {
#         "Content-Type": "text/xml; charset=UTF-8"
#     }

#     # Client needs to be closed after request
#     with httpx.Client() as client:
#         response = client.post(URL, content=body, headers=headers)

#         response = response.text
#         return response


# Using this to receive response as a dict
def check_vies_vat(country: str, nip: str):
    WSDL = "https://ec.europa.eu/taxation_customs/vies/services/checkVatService.wsdl"

    client = Client(wsdl=WSDL)

    result = client.service.checkVat(countryCode=country, vatNumber=nip)
    
    result_dict = serialize_object(result)

    return result_dict


data = check_vies_vat('PL', "9551464208")

print(data)