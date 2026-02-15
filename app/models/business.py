from sqlalchemy import String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as PyUUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
import uuid
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.base import Base


class BusinessCheck(Base):
    __tablename__ = 'business_check'

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tax_id: Mapped[str] = mapped_column(String(20), index=True, nullable=False)     # NIP, index=True for most searched values
    company_name: Mapped[str] = mapped_column(String(255))
    is_vat_active: Mapped[bool] = mapped_column(Boolean, default=False)
    # Field for the rest answer
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False)    # JSONB (binary) takes more space, but works faster

    # For Database Caching
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())   # server_default=func.now() uses Postgres exact time, same for all records
    owner_id: Mapped[PyUUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # For relation with users table, like related_name in Django
    # Mapped["User"] is defining class Name
    # back_populates is for creating a connection with var from User class
    owner: Mapped["User"] = relationship("User", back_populates="business_check")
