from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.token import TokenPayload
from app.clients.auth_client import verify_token


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    return await verify_token(token)

def get_current_user_id(
    payload: TokenPayload = Depends(get_current_user),
) -> UUID:
    return UUID(payload.sub)


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_id",
]