from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.status import HealthCheck
from app.schemas.status import SystemStatus
from app.services.health_service import check_vies_health
from app.db.deps import get_db
from app.core.limiter import limiter
from fastapi import Request

router = APIRouter()


@router.get("/status", summary="Get system health status", response_model=SystemStatus)
@limiter.limit("10/minute")
async def get_system_status(request: Request, db: AsyncSession = Depends(get_db)):
    vies_status = await check_vies_health()

    new_status = HealthCheck(
        service=vies_status.get("service"),
        status=vies_status.get("status"),
        latency_ms=vies_status.get("latency_ms")
    )

    db.add(new_status)

    await db.commit()
    await db.refresh(new_status)

    return new_status
