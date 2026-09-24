from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class EmployeeFields(BaseModel):
    """Shared input fields with whitespace and case normalization."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=100)
    primary_skill: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=100)
    work_mode: Literal["WFH", "WFO"]

    @field_validator("name", "department", "primary_skill", "location", mode="before")
    @classmethod
    def required_text_must_not_be_blank(cls, value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("This field must not be empty or whitespace only")
        return value.strip()

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class EmployeeCreate(EmployeeFields):
    pass


class EmployeeUpdate(EmployeeFields):
    is_active: bool


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    department: str
    primary_skill: str
    location: str
    work_mode: Literal["WFH", "WFO"]
    is_active: bool
    created_at: datetime


class EmployeeListResponse(BaseModel):
    """A page of employees together with pagination metadata."""

    total: int = Field(..., ge=0, description="Matching employees before pagination")
    limit: int = Field(..., ge=1, le=100, description="Requested page size")
    offset: int = Field(..., ge=0, description="Requested number of records to skip")
    items: list[EmployeeResponse]
