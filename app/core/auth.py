from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings
from app.core.security import pwd_context
from fastapi.security import APIKeyHeader
import secrets

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)    # If no API Key in request error 403


def generate_new_api_key() -> str:
    """
    Generates unique randomized API Key
    """
    return secrets.token_hex(32)


def verify_api_key_hash(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    Verifies if provided API Key matches value in DB
    """
    return pwd_context.verify(plain_api_key[:72], hashed_api_key)


def create_access_token(data: dict):
    """
    Creates signed token JWT.
    'data' is a dict for sending for example {"sub": str(user.id)}
    """
    # For safety creating copy
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str):
    """
    Function to decode token. Gets 'sub' and 'expire'
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM] # list for safety and flexibility
        )
        if payload.get("type") != "access":
            return None

        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict):
    """
    Fuction creates refresh token
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(
        to_encode,
        settings.REFRESH_TOKEN_KEY,     # Different key
        algorithm=settings.JWT_ALGORITHM
    )


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.REFRESH_TOKEN_KEY,
            algorithms=[settings.JWT_ALGORITHM] # list for safety and flexibility
        )
        if payload.get("type") != "refresh":
            return None

        return payload
    except JWTError:
        return None
