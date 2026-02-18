from pydantic import BaseModel


class SystemStatus(BaseModel):
    service: str
    status: str
    latency_ms: int | None = None