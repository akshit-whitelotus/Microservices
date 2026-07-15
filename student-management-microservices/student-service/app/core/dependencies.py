from __future__ import annotations

from uuid import UUID

from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.clients.auth_client import verify_token
from app.core.database import get_db
from app.schemas.token import TokenPayload


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
  

    token = credentials.credentials

    payload = await verify_token(token)
    try:
        return TokenPayload.model_validate(payload)

    except Exception:
        raise HTTPException(
        status_code=401,
        detail="Invalid authentication payload.",
    )


def get_current_user_id(
    payload: TokenPayload = Depends(get_current_user),
) -> UUID:
    """
    Convenience dependency that returns the authenticated user's UUID.
    """

    return UUID(payload.sub)


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_id",
]