from __future__ import annotations

from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from app.clients.auth_client import verify_token
from app.core.database import get_db
from app.schemas.token import TokenPayload


security = HTTPBearer(auto_error=True)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:

    token = credentials.credentials

    try:
        payload = await verify_token(token)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    try:
        return TokenPayload.model_validate(payload)

    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication payload.",
        )

def get_current_user_id(
    payload: TokenPayload = Depends(get_current_user),
) -> UUID:

    return UUID(payload.sub)


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_id",
]