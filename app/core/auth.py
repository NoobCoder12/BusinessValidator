from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings


def create_access_token(data: dict):
    """
    Creates signed token JWT.
    'data' is a dict for sending for example {"sub": str(user.id)}
    """
    # For safety creating copy
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)

    to_encode.update({"exp": expire})

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
        return payload
    except JWTError:
        return None
