"""
JWT security utilities.

Responsibilities
----------------
- Validate JWT access tokens
- Verify signature
- Verify expiration
- Verify issuer
- Verify audience

The Student Service NEVER creates tokens.
It only validates tokens issued by the Auth Service.
"""

from __future__ import annotations

from jose import JWTError
from jose import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.schemas.token import TokenPayload


def decode_access_token(
    token: str,
) -> TokenPayload:
    """
    Validate and decode a JWT access token.

    Raises:
        UnauthorizedException
    """

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )

        return TokenPayload.model_validate(payload)

    except JWTError as exc:
        raise UnauthorizedException(
            message="Invalid or expired access token.",
        ) from exc