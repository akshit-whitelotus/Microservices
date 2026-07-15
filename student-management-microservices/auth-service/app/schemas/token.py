"""
JWT token response schemas.

Responsibilities
----------------
- Define authentication response models.
- Used by the login endpoint.
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class Token(BaseModel):
    """
    JWT access token response.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    access_token: str = Field(
        description="JWT access token"
    )

    token_type: str = Field(
        default="bearer",
        description="Token type"
    )


class TokenPayload(BaseModel):
    """
    JWT payload after decoding.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    sub: str
    iss: str
    aud: str
    exp: int
    iat: int