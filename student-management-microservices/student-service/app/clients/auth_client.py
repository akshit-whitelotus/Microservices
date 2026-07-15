

from __future__ import annotations

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


async def verify_token(token: str) -> dict:

    print("AUTH URL USED:", settings.AUTH_SERVICE_URL)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )

    except httpx.RequestError as exc:
        print("AUTH SERVICE CONNECTION ERROR:", repr(exc))

        raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Authentication service is unavailable.",
    )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    return response.json()