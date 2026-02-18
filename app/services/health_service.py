import httpx
import time


async def check_vies_health() -> dict:
    url = "https://ec.europa.eu/taxation_customs/vies/services/checkVatService.wsdl"
    start_time = time.perf_counter()    # Current time in seconds

    try:
        async with httpx.AsyncClient() as client:   # Connection must be closed
            response = await client.get(url, timeout=5.0)
            latency = int((time.perf_counter() - start_time) * 1000)    # Converting time difference to ms

            if response.status_code == 200:
                return {
                    "service": "VIES",
                    "status": "operational",
                    "latency_ms": latency
                    }
            return {
                    "service": "VIES",
                    "status": "degraded",
                    "latency_ms": latency
                    }

    except Exception:
        return {
                    "service": "VIES",
                    "status": "down",
                    "latency_ms": None
                    }