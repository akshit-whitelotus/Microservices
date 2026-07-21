from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html

import httpx

from app.core.config import settings
from app.proxy import proxy_request
from app.openapi_merge import merged_openapi
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Unified Gateway API",
    docs_url=None,
    openapi_url=None,
)

# The frontend authenticates with a Bearer token (not cookies), so we don't
# need allow_credentials=True here. That means we can safely allow any
# origin -- which also fixes the case where the frontend is opened directly
# as a local file (Origin: null) or served from a port/host not in a fixed
# whitelist. Previously this list only allowed http://localhost:3000 and
# http://127.0.0.1:5500, so every request from anywhere else (including
# file:// pages) was silently blocked by the browser after a successful
# response from the server -- this was the actual cause of "login not
# working" and the rest of the frontend failing along with it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# OpenAPI
# -------------------------------

@app.get("/openapi.json")
async def openapi():

    return await merged_openapi(
        settings.AUTH_SERVICE_URL,
        settings.STUDENT_SERVICE_URL,
        settings.DOCUMENT_SERVICE_URL
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
# DOCUMENT PROXY
# -------------------------------


@app.api_route(
    "/api/v1/documents",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
@app.api_route(
    "/api/v1/documents/",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
@app.api_route(
    "/api/v1/documents/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
async def document_proxy(
    request: Request,
):

    return await proxy_request(
        request,
        settings.DOCUMENT_SERVICE_URL,
    )

# -------------------------------
# HEALTH
# -------------------------------

@app.get("/health")
async def health():

    services = {}


    targets = {

        "auth":
        settings.AUTH_SERVICE_URL,


        "student":
        settings.STUDENT_SERVICE_URL,


        "document":
        settings.DOCUMENT_SERVICE_URL,

    }


    async with httpx.AsyncClient(
        timeout=settings.REQUEST_TIMEOUT_SECONDS
    ) as client:


        for name,url in targets.items():

            try:

                response = await client.get(
                    f"{url}/health"
                )


                services[name] = {

                    "status":
                    "healthy",

                    "response":
                    response.json(),

                }


            except httpx.RequestError:


                services[name] = {

                    "status":
                    "unreachable"

                }



    overall = (
        "healthy"
        if all(
            x["status"]=="healthy"
            for x in services.values()
        )
        else
        "degraded"
    )


    return {

        "gateway":
        "healthy",

        "overall":
        overall,

        "services":
        services,

    }