"""
Student schemas.

Responsibilities
----------------
- Validate incoming requests.
- Define API response models.
- No business logic.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator


# ---------------------------------------------------------
# Base Schema
# ---------------------------------------------------------

class StudentBase(BaseModel):
    """
    Common student fields.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    first_name: str = Field(
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    course: str = Field(
        min_length=2,
        max_length=150,
    )

    enrollment_year: int = Field(
        ge=2000,
        le=2100,
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Name must contain only alphabetic characters."
            )

        return value.title()


# ---------------------------------------------------------
# Create
# ---------------------------------------------------------

class StudentCreate(StudentBase):
    """
    Request body for student creation.
    """

    pass


# ---------------------------------------------------------
# Partial Update
# ---------------------------------------------------------

class StudentUpdate(BaseModel):
    """
    PATCH request body.

    Every field is optional.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    course: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    enrollment_year: int | None = Field(
        default=None,
        ge=2000,
        le=2100,
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return value

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Name must contain only alphabetic characters."
            )

        return value.title()


# ---------------------------------------------------------
# Response
# ---------------------------------------------------------

class StudentResponse(BaseModel):
    """
    Student response model.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    first_name: str

    last_name: str

    email: EmailStr

    course: str

    enrollment_year: int

    created_at: datetime

    updated_at: datetime


# ---------------------------------------------------------
# Paginated Response
# ---------------------------------------------------------

class StudentListResponse(BaseModel):
    """
    Paginated list response.
    """

    items: list[StudentResponse]

    total: int

    page: int

    page_size: int