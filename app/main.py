from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.schemas.user import UserCreate, UserOut
from app.db.deps import get_db
from app.models.user import User
from app.core.security import pwd_context


app = FastAPI()


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
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
