from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.auth import decode_access_token, api_key_header, verify_api_key_hash
import redis.asyncio as redis
from typing import AsyncGenerator
import sentry_sdk


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")     # Gets Bearer and Token from Authorization header and passes to function

# Connection Pooling for Redis requests
redis_pool = redis.ConnectionPool.from_url("redis://localhost:6379", decode_responses=True)


async def get_db():
    # async with will close session after finish
    async with AsyncSessionLocal() as session:
        yield session


# [] means it created sort of things between the brackets
# First argument is what we generate with yield
# Second argument in [] means value that we return - we don't need to return anything
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    Creating a client for pooling
    """
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    # Gets Bearer and Token from Authorization header and passes to function. Lock icon with show in swagger
    token: str = Depends(oauth2_scheme)
) -> User:
    cred_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_access_token(token)
    if payload is None:
        raise cred_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise cred_exception

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise cred_exception

    sentry_sdk.set_user({"id": user.id, "username": user.username})     # Set logging for certain user

    return user


async def get_user_by_api_key(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(api_key_header)
) -> User:

    query = select(User).where(User.api_key_hashed != None)     # Get users with API Key first
    result = await db.execute(query)
    users = result.scalars().all()

    for user in users:
        is_valid = verify_api_key_hash(api_key, user.api_key_hashed)    # verify() gets hashing metod and recreates it
        if is_valid:
            sentry_sdk.set_user({"id": user.id, "username": user.username})
            return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API Key"
    )
