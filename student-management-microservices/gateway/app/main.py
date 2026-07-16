from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html

import httpx

from app.core.config import settings
from app.proxy import proxy_request
from app.openapi_merge import merged_openapi


app = FastAPI(
    title="Unified Gateway API",
    docs_url=None,
    openapi_url=None,
)



# -------------------------------
# OpenAPI
# -------------------------------

@app.get("/openapi.json")
async def openapi():

    return await merged_openapi(
        settings.AUTH_SERVICE_URL,
        settings.STUDENT_SERVICE_URL,
    )



@app.get("/docs")
async def docs():

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Gateway Docs",
    )



# -------------------------------
# AUTH PROXY
# -------------------------------

@app.api_route(
    "/api/v1/auth",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
@app.api_route(
    "/api/v1/auth/",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
@app.api_route(
    "/api/v1/auth/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
async def auth_proxy(
    request: Request,
):

    return await proxy_request(
        request,
        settings.AUTH_SERVICE_URL,
    )



# -------------------------------
# STUDENT PROXY
# -------------------------------

@app.api_route(
    "/api/v1/students",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
@app.api_route(
    "/api/v1/students/",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
@app.api_route(
    "/api/v1/students/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
async def student_proxy(
    request: Request,
):

    return await proxy_request(
        request,
        settings.STUDENT_SERVICE_URL,
    )



# -------------------------------
# HEALTH
# -------------------------------

@app.get("/health")
async def health():

    services = {}


    async with httpx.AsyncClient(
        timeout=settings.REQUEST_TIMEOUT_SECONDS
    ) as client:


        # AUTH
        try:

            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/health"
            )

            services["auth"] = {
                "status": "healthy",
                "response": response.json(),
            }


        except httpx.RequestError:

            services["auth"] = {
                "status": "unreachable"
            }



        # STUDENT
        try:

            response = await client.get(
                f"{settings.STUDENT_SERVICE_URL}/api/v1/health"
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