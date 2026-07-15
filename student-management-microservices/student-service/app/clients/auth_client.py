import httpx
from fastapi import HTTPException

AUTH_SERVICE_URL = "http://127.0.0.1:8002"


async def verify_token(token: str):

    print("TOKEN RECEIVED IN STUDENT SERVICE:")
    print(token)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/api/v1/auth/verify",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    print("AUTH SERVICE STATUS:", response.status_code)
    print("AUTH SERVICE RESPONSE:", response.text)

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return response.json()