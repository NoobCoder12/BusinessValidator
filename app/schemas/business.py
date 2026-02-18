from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.core.validators import validate_nip, validate_regon
from uuid import UUID
from datetime import datetime
from typing import Optional


class BusinessCheckCreate(BaseModel):
    tax_id: str = Field(..., min_length=10, max_length=10)            # '...' field is obligatory
    regon: str | None = Field(None, min_length=9, max_length=9)

    @field_validator("tax_id")
    @classmethod
    def validate_tax_id(cls, v: str) -> str:
        return validate_nip(v)

    @field_validator("regon")
    @classmethod
    def validate_regon(cls, v: str) -> str:
        if v:
            return validate_regon(v)
        return v


class BusinessCheckOut(BaseModel):
    id: UUID
    tax_id: str
    company_name: Optional[str]
    is_vat_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
