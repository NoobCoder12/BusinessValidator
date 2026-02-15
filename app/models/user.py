from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from uuid import UUID as PyUUID
from app.db.base import Base

# SQLAlchemy 2.0 style
# Mapped[] defines data type
# mapped_column defines table field


class User(Base):
    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)    # UUID for safety, ID will not be predictable
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    # Creating relationship with business_checl
    business_check: Mapped[list["BusinessCheck"]] = relationship("BusinessCheck", back_populates="owner", cascade="all, delete-orphan") # cascade works on Python level