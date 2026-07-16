"""
JWT security utilities.

Student Service only validates
tokens issued by Auth Service.
"""

from __future__ import annotations


from shared.auth.jwt import (
    decode_access_token as decode_jwt_token
)

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.schemas.token import TokenPayload


def decode_access_token(
    token: str,
) -> TokenPayload:

    try:

        payload = decode_jwt_token(
            token=token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )

        return TokenPayload.model_validate(
            payload
        )


    except Exception as exc:

        raise UnauthorizedException(
            message="Invalid or expired access token.",
        ) from exc