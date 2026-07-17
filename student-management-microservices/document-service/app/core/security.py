from __future__ import annotations


from shared.auth.jwt import (
    decode_access_token,
)

from app.core.config import settings



def decode_token(
    token: str,
) -> dict | None:

    try:

        return decode_access_token(
            token=token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )

    except Exception:

        return None