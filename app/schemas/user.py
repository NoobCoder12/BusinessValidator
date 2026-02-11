from pydantic import BaseModel, EmailStr, ConfigDict

# User model separation. Prevents API to return users password


# Data user sends
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str | None = None


# Data API returns
class UserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str | None = None

    # model_config lets Pydantic read data from ORM objects instead of waiting for dicts
    model_config = ConfigDict(from_attributes=True)