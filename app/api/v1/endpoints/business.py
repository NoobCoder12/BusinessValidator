from fastapi import APIRouter, Depends, Request, Response
from app.schemas.business import BusinessCheckOut, BusinessCheckCreate
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.db.deps import get_db, get_user_by_api_key, get_redis
from app.models.user import User
from app.models.business import BusinessCheck
from app.services.vies_service import check_vies_vat
from sqlalchemy import select, func, desc
from datetime import datetime, timezone, timedelta
from app.core.limiter import limiter
from app.core.logging import logger
import json

router = APIRouter()


@router.post("/validate", response_model=BusinessCheckOut)  # Prevents from returning all data about business from db
@limiter.limit("10/minute")
async def validate_business(
    request: Request,       # For rate limiter
    response: Response,     # For displaying rate limiter
    check_in: BusinessCheckCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_user_by_api_key)
):

    nip = check_in.tax_id
    cache_key = f"bus:v1:{nip}"      # Key for Redis, all keys are in the same place
    data = None

    # Check redis first, no need to do API request if result is in base
    try:
        cached_val = await redis_client.get(cache_key)
        if cached_val:
            data = json.loads(cached_val)
            logger.info(f"Data retrieved from Redis by {current_user.email} for {nip}")

    except Exception as e:
        logger.warning(f"Error while fetching data from Redis: {e}")

    # If there is no result in redis
    if not data:
        time_ago = datetime.now(timezone.utc) - timedelta(days=10)
        query = (
            select(BusinessCheck)
            .where(BusinessCheck.tax_id == nip, BusinessCheck.created_at > time_ago)
            .order_by(BusinessCheck.created_at.desc())
            .limit(1)
        )

        result_db_check = await db.execute(query)
        result_from_db = result_db_check.scalar_one_or_none()

        if result_from_db:
            # Preventing possibility to see other's user ID in raw_data
            data = {
                "name": result_from_db.company_name,
                "vat_number": result_from_db.tax_id,
                "is_valid": result_from_db.is_vat_active
            }

            # We don't want to refresh 10 days
            expiration_date = result_from_db.created_at + timedelta(days=10)
            remaining_time = expiration_date - datetime.now(timezone.utc)

            ttl_seconds = int(remaining_time.total_seconds())

            if ttl_seconds > 0:
                # Save result to redis for next request
                try:
                    await redis_client.setex(       # setex(key, exp, value)
                        cache_key,
                        ttl_seconds,
                        json.dumps(data)
                    )
                    logger.info(f"Result for ID {nip} saved to redis")
                except Exception as e:
                    logger.warning(f"Could not save result to redis: {e}")

            logger.info(f"Data requested from DB for user: {current_user.username}")

    # API request if no result in redis and DB
    if not data:
        data = check_vies_vat("PL", nip)
        # nip validaton on outer service
        logger.info(f"Data requested from API by {current_user.username} for {nip}")

        # Save result to redis for next request
        try:
            await redis_client.setex(       # setex(key, exp, value)
                cache_key,
                timedelta(days=10),
                json.dumps(data)
            )
            logger.info(f"Result for ID {nip} saved to redis")
        except Exception as e:
            logger.warning(f"Could not save result to redis: {e}")

        logger.info(f"Data requested from API for user: {current_user.username}")

    # Making sure that user id will be correct
    clean_data = dict(data)
    clean_data["owner_id"] = str(current_user.id)

    new_record = BusinessCheck(
        tax_id=nip,
        company_name=data.get("name"),
        is_vat_active=data.get("is_valid"),
        owner_id=current_user.id,
        raw_data=clean_data,
    )

    # Save result to DB
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    logger.info(f"Check was created and saved in DB for user: {current_user.username}")
    return new_record


@router.get("/history", response_model=list[BusinessCheckOut], summary="Get your validation history")
@limiter.limit("30/minute")
async def get_user_history(
    request: Request,
    response: Response,
    # Settings for pagination
    skip: int = 0,     # Start from 0
    limit: int = 10,    # Inspect 10 records at once
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_by_api_key)
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

    logger.info(f"History was retrieved from DB for user: {current_user.username}")
    return checks


@router.get("/stats/me", summary="Get statistics of your searches")
@limiter.limit("30/minute")
async def get_stats_me(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_by_api_key)
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

    logger.info(f"Stats were retrieved from DB for user: {current_user.username}")
    return {
        "total_searches": count,
        "most_searched": most_searched_data,
        "active_vat_pct": percent_of_active,
        "last_activity": last_activity
    }
