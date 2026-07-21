from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app.core.security import decode_token
from app.schemas.token import TokenPayload
from shared.auth.dependencies import require_roles


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """
    Decode JWT and return current user.
    """

    payload = decode_token(
        credentials.credentials
    )

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    try:
        return TokenPayload(
            sub=payload["sub"],
            role=payload["role"],
            exp=payload["exp"],
            iat=payload["iat"],
            iss=payload["iss"],
            aud=payload["aud"],
        )
    except (KeyError, ValueError):
        # A well-signed token that's still missing/malformed claims
        # (e.g. no "role") is an authentication failure, not a server
        # error.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication payload",
        )



require_teacher = require_roles(
    "teacher",
    get_current_user=get_current_user,
)