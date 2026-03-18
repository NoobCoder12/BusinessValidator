from fastapi import APIRouter, status, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request
from sqlalchemy.exc import IntegrityError

from app.schemas.user import UserCreate, UserOut
from app.db.deps import get_db, get_current_user
from app.models.user import User
from app.core.security import pwd_context, verify_password, get_password_hash
from app.core.auth import create_access_token, create_refresh_token, verify_refresh_token, generate_new_api_key
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import logger

router = APIRouter()


@router.post("/register", summary="Register a new user account", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register_user(
    request: Request,
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):

    # Checking if users email is already taken
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    exisiting_user = result.scalar_one_or_none()    # Returns one or none, error if more

    if exisiting_user:
        logger.warning(f"Duplicating email for user: {exisiting_user.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # User passed email check
    hashed_pass = pwd_context.hash(user_in.password)
    target_username = user_in.username if user_in.username else user_in.email

    new_user = User(
        email=user_in.email,
        username=target_username,
        password=hashed_pass)

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)  # Gets ID from DB
    except IntegrityError as e:
        await db.rollback()     # Cancel failed trasaction
        logger.error(f"Integrity error during registration: {str(e)}")

        error_msg = str(e.orig).lower()
        if "users_username_key" in error_msg:
            raise HTTPException(status_code=400, detail="Username already taken")
        if "users_email_key" in error_msg:
            raise HTTPException(status_code=400, detail="Email already registered")

        raise HTTPException(status_code=400, detail="Registration failed - data conflict")

    logger.info(f"User {new_user.username} registered and saved to DB")

    return new_user


@router.post("/token", summary="Login to get access token. If no username provided user email")
@limiter.limit("10/minute")
async def login_for_access_token(
    request: Request,   # Limiter needs an access to request
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):

    query = select(User).where(
        or_(    # better practice for sqlalchemy
            User.username == form_data.username,
            User.email == form_data.username    # username comes from OAuth2PasswordRequestForm, user provides email
            )
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password):
        logger.warning(f"Wrong logging credentials for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": str(user.id)})      # str for safety issues
    refresh_token = create_refresh_token(data={"sub": str(user.id)}) 

    secure = settings.ENV == "production"   # Value is overwritten on Cloud
    
    # Create cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,              # For safety, JS won't get that
        secure=secure,               # False for development, True for production
        samesite="lax",             # Prevents CSRF
        max_age=settings.REFRESH_ACCESS_TOKEN_EXPIRE * 3600 * 24
    )

    logger.info(f"Tokens for user {user.username} created and saved")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut, summary="Get your user data")
@limiter.limit("10/minute")
async def read_user_me(
    request: Request, 
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint will let you trough only with valid token.
    Returns data of current user
    """
    logger.info(f"Returning account info for user: {current_user.username}")
    return current_user


@router.post("/refresh", summary="Refresh access token using cookie")
@limiter.limit("10/minute")
async def refresh_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    refresh_token: str = Cookie(None)       # FastAPI will look for refresh_token, it is optional
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token found")  # Valid message thanks to None in Cookie

    payload = verify_refresh_token(refresh_token)
    if not payload:
        logger.warning("Attempted refresh with invalid or expired token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or is not valid")

    user_id: str = payload.get("sub")

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Refresh failed for user {user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist")

    new_access_token = create_access_token(data={"sub": str(user_id)})

    logger.info(f"Access token refreshed for user: {user.username}")
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout", summary="Logout and delete refresh token cookie")
@limiter.limit("10/minute")
async def logout(
    request: Request,
    response: Response
):
    """
    Deletes cookie from browser.
    Access token still lives, but won't be refreshed.
    """

    secure = settings.ENV == "production"   # Value is overwritten on Cloud

    response.delete_cookie(
        key="refresh_token",
        httponly=True,              # For safety, JS won't get that
        secure=secure,               # False for development, True for production
        samesite="lax"              # Prevents CSRF
    )

    logger.info("Refresh cookie was deleted for logout")
    return {"detail": "Successfully logged out"}


@router.post("/me/api-key", summary="Generate or rotate API key")
@limiter.limit("10/minute")
async def create_user_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    raw_key = generate_new_api_key()

    current_user.api_key_hashed = get_password_hash(raw_key)    # Same function as for password

    await db.commit()
    await db.refresh(current_user)

    logger.info(f"User {current_user.username} created API Key and save it in DB")
    return {
        "api_key": raw_key
    }