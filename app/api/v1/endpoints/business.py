from fastapi import APIRouter, Depends, Request
from app.schemas.business import BusinessCheckOut, BusinessCheckCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db, get_current_user
from app.models.user import User
from app.models.business import BusinessCheck
from app.services.vies_service import check_vies_vat
from sqlalchemy import select, func, desc
from app.core.limiter import limiter

router = APIRouter()


@router.post("/validate", response_model=BusinessCheckOut)  # Prevents from returning all data about business from db
@limiter.limit("10/minute")
async def validate_business(
    request: Request,
    check_in: BusinessCheckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    nip = check_in.tax_id

    result = check_vies_vat("PL", nip)
    # nip validaton on outer service

    new_record = BusinessCheck(
        tax_id=nip,
        company_name=result.get("name"),
        is_vat_active=result.get("is_valid"),
        owner_id=current_user.id,
        raw_data=result,
    )

    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    return new_record


@router.get("/history", response_model=list[BusinessCheckOut])
@limiter.limit("30/minute")
async def get_user_history(
    request: Request,
    # Settings for pagination
    skip: int = 0,     # Start from 0
    limit: int = 10,    # Inspect 10 records at once
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = (
        select(BusinessCheck)
        .where(BusinessCheck.owner_id == current_user.id)
        .order_by(BusinessCheck.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)

    checks = result.scalars().all()

    if not checks:
        return []

    return checks


@router.get("/stats/me", description="Get statistics of your searches")
@limiter.limit("30/minute")
async def get_stats_me(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Query for all searches count
    query = select(func.count(BusinessCheck.id)).where(BusinessCheck.owner_id == current_user.id)
    result_prep = await db.execute(query)
    count = result_prep.scalar()

    # Query for most searched position
    query_most_searched = (
        select(BusinessCheck.tax_id, func.count(BusinessCheck.id).label("count"))
        .where(BusinessCheck.owner_id == current_user.id)
        .group_by(BusinessCheck.tax_id)
        .order_by(desc("count"))
        .limit(1)
    )
    result_most = await db.execute(query_most_searched)

    row = result_most.first()   # Getting a row to extract the data

    most_searched_data = None

    if row:
        most_searched_data = {
            "tax_id": row.tax_id,
            "count": row.count
        }

    # Query for active VAT count
    query_active_vat = (
        select(func.count(BusinessCheck.id))
        .where(BusinessCheck.owner_id == current_user.id)
        .where(BusinessCheck.is_vat_active == True)
        )

    result_active = await db.execute(query_active_vat)
    number_actice = result_active.scalar()

    percent_of_active = f"{(number_actice / count) * 100:.2f}%" if count > 0 else "0.00%"

    # Query for last activity
    query_activity = (
        select(BusinessCheck.tax_id, BusinessCheck.created_at.label("date"))
        .where(BusinessCheck.owner_id == current_user.id)
        .order_by(desc("date"))
        .limit(1)
    )

    result_last_activity = await db.execute(query_activity)
    row_activity = result_last_activity.first()

    last_activity = None
    if row_activity:
        last_activity = {
            "tax_id": row_activity.tax_id,
            "check_date": row_activity.date
        }

    return {
        "total_searches": count,
        "most_searched": most_searched_data,
        "active_vat_pct": percent_of_active,
        "last_activity": last_activity
    }
