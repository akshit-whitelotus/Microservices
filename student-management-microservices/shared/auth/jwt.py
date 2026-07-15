"""
Shared JWT helper.

Both Auth Service and Student Service
use exactly the same JWT implementation.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError


def create_access_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
    issuer: str,
    audience: str,
) -> str:

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=expires_minutes
    )

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
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
) -> dict:

    return jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
        issuer=issuer,
        audience=audience,
    )