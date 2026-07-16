import pytest
import httpx

from fastapi.testclient import TestClient
from app.core.config import settings

from app.main import app


client = TestClient(app)


def test_proxy_auth(httpx_mock):

    httpx_mock.add_response(
        method="GET",
        url="http://localhost:8002/api/v1/auth/users",
        status_code=200,
        json={
            "users": []
        },
    )

    response = client.get(
        "/api/v1/auth/users"
    )

    assert response.status_code == 200

    assert response.json() == {
        "users": []
    }



def test_downstream_error_passthrough(httpx_mock):

    httpx_mock.add_response(
        method="GET",
        url="http://localhost:8001/api/v1/students/",
        status_code=404,
        json={
            "detail": "not found"
        },
    )

    response = client.get(
        "/api/v1/students"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "not found"
    }



@app.get("/health")
async def health():

    services = {}

    async with httpx.AsyncClient(
        timeout=settings.REQUEST_TIMEOUT_SECONDS
    ) as client:


        # AUTH SERVICE
        try:

            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/health"
            )

            services["auth"] = {
                "status": "healthy",
                "response": response.json(),
            }


        except httpx.RequestError:

            services["auth"] = {
                "status": "unreachable"
            }



        # STUDENT SERVICE
        try:

            response = await client.get(
                f"{settings.STUDENT_SERVICE_URL}/health"
            )

            services["students"] = {
                "status": "healthy",
                "response": response.json(),
            }


        except httpx.RequestError:

            services["students"] = {
                "status": "unreachable"
            }



    overall = (
        "healthy"
        if all(
            service["status"] == "healthy"
            for service in services.values()
        )
        else "degraded"
    )


    return {
        "gateway": "healthy",
        "overall": overall,
        "services": services,
    }