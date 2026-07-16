from __future__ import annotations

import httpx

from fastapi import HTTPException, status

from app.core.config import settings


async def verify_token(token: str) -> dict:

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:

            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )

    except httpx.RequestError:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable.",
        )


    if response.status_code == 200:
        return response.json()


    if response.status_code in (401, 403):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )


    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Authentication service error.",
    )