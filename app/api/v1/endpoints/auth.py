from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm


from app.schemas.user import UserCreate, UserOut
from app.db.deps import get_db, get_current_user
from app.models.user import User
from app.core.security import pwd_context, verify_password
from app.core.auth import create_access_token
from app.db.deps import oauth2_scheme

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):

    # Checking if users email is already taken
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    exisiting_user = result.scalar_one_or_none()    # Returns one or none, error if more

    if exisiting_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # User passed email check
    hashed_pass = pwd_context.hash(user_in.password)

    new_user = User(
        email=user_in.email,
        username=user_in.nickname or user_in.email.split("@")[0],
        password=hashed_pass)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  # Gets ID from DB

    return new_user


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):

    query = select(User).where(User.email == form_data.username)    # username comes from OAuth2PasswordRequestForm, user provides email
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": str(user.id)})      # str for safety issues

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Endpoint will let you trough only with valid token.
    Returns data of current user
    """

    return current_user