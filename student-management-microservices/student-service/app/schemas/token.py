"""
JWT token schemas.

Responsibilities
----------------
- Represent JWT payload after validation.
- Shared by dependencies and security modules.
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict


class TokenPayload(BaseModel):
    """
    Decoded JWT payload.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    sub: str
    iss: str
    aud: str
    exp: int
    iat: int