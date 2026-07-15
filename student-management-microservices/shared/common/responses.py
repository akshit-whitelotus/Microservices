"""
Shared API response envelopes.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErrorBody(BaseModel):

    code: str

    message: str

    details: Any | None = None


class ErrorResponse(BaseModel):

    error: ErrorBody