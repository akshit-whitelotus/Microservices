from fastapi import Request
from fastapi.responses import Response, JSONResponse
import httpx

from app.core.config import settings


HOP_BY_HOP_HEADERS = {
    "connection",
    "host",
    "transfer-encoding",
    "content-length",
}


def clean_headers(headers):

    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }



def downstream_path(path: str) -> str:

    """
    Convert gateway paths to service paths.

    Gateway:
        /api/v1/students
        /api/v1/auth/login

    Downstream:
        /students
        /auth/login
    """

    if path.startswith("/api/v1/students"):
        new_path = path.replace(
            "/api/v1/students",
            "/students",
            1,
        )

        return new_path or "/students"
    if path.startswith(
        "/api/v1/documents"
    ):

        return path.replace(
            "/api/v1/documents",
            "/documents",
            1,
        ) or "/documents"


    if path.startswith("/api/v1/auth"):

        new_path = path.replace(
            "/api/v1/auth",
            "/api/v1/auth",
            1,
        )

        return new_path


    return path



async def proxy_request(
    request: Request,
    target_url: str,
):

    path = downstream_path(
        request.url.path
    )


    url = f"{target_url}{path}"


    if request.url.query:
        url += f"?{request.url.query}"


    body = await request.body()


    headers = clean_headers(
        request.headers
    )
    headers["X-INTERNAL-SERVICE-KEY"] = (
    settings.INTERNAL_SERVICE_SECRET
)


    print(
        "FORWARDING:",
        request.method,
        url,
    )


    try:

        async with httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        ) as client:


            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
            )


        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=clean_headers(
                response.headers
            ),
        )


    except httpx.RequestError:

        return JSONResponse(
            status_code=503,
            content={
                "error":
                "Downstream service unavailable"
            },
        )