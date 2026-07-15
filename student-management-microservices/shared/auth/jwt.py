"""
Shared JWT helper.

Both Auth Service and Student Service
use exactly the same JWT implementation.
"""

from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import jwt


def create_access_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
    issuer: str,
    audience: str,
) -> str:

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=expires_minutes
    )

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": issuer,
        "aud": audience,
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm,
    )


def decode_access_token(
    *,
    token: str,
    secret_key: str,
    algorithm: str,
    issuer: str,
    audience: str,
):

    return jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
        issuer=issuer,
        audience=audience,
    )