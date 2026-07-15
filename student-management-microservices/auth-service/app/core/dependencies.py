from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenPayload


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


# ---------------------------------------------------------
# Token Payload Dependency
# ---------------------------------------------------------

async def get_token_payload(
    token: str = Depends(oauth2_scheme),
) -> TokenPayload:
    """
    Validate JWT and return decoded claims.
    """

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


    try:
        return TokenPayload.model_validate(payload)

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )


# ---------------------------------------------------------
# Current User Dependency
# ---------------------------------------------------------

async def get_current_user(
    payload: TokenPayload = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db),
):

    user_id = payload.sub

    repo = UserRepository(db)

    user = await repo.get_by_id(
        int(user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user