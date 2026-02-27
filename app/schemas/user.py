from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
from uuid import UUID
import re

# User model separation. Prevents API to return users password


# Data user sends
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100, description="""Password must contain:
                          - at least 8 character
                          - at least one lowercase letter
                          - at least one uppercase letter
                          - at least one digit""")
    username: str | None = Field(None, description="User's public display name")    # Field is better than 'str', allows setting it up

    @field_validator("password")
    @classmethod                        # Checks condidtions before creating class
    def password_complexity(cls, v: str) -> str:
        # For lower char
        if not re.search("[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        # For upper char
        if not re.search("[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        # For digit
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        # For special char
        if not re.search(r"[!@#$%&*_,./]", v):
            raise ValueError("Password must contain at least one special character")

        return v


# Data API returns
class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    username: str | None = None

    # model_config lets Pydantic read data from ORM objects instead of waiting for dicts
    model_config = ConfigDict(from_attributes=True)