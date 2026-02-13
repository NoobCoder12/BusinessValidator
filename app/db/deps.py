from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.auth import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")     # Gets Bearer and Token from Authorization header and passes to function


async def get_db():
    # async with will close session after finish
    async with AsyncSessionLocal() as session:
        yield session


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

    return user
