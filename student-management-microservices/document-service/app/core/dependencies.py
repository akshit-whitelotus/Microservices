from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app.core.security import decode_token
from app.schemas.token import TokenPayload


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


    return TokenPayload(
        sub=payload["sub"],
        role=payload["role"],
        exp=payload["exp"],
        iat=payload["iat"],

        iss=payload["iss"],
        aud=payload["aud"],
    )



def require_teacher(
    current_user: TokenPayload = Depends(
        get_current_user
    ),
) -> TokenPayload:
    """
    Allow only teacher role.
    """

    if current_user.role != "teacher":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher role required",
        )


    return current_user