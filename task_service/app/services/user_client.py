import httpx
from fastapi import HTTPException

USER_SERVICE_URL="http://localhost:8001"

async def verify_user(user_id:int):
    async with httpx.AsyncClient() as client:
        response=await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404,detail="User Not Found")
        if response.status_code !=200:
            raise HTTPException(status_code=500,detail="User Service Unavaible")
        return response.json()

