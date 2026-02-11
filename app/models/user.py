from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from app.db.base import Base

# SQLAlchemy 2.0 style


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)