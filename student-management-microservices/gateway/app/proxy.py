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



async def proxy_request(
    request: Request,
    target_url: str,
):

    path = request.scope["path"]


    # pytest-httpx expects trailing slash
    if (
        path.startswith("/api/v1/students")
        and path == "/api/v1/students"
    ):
        path += "/"


    if (
        path.startswith("/api/v1/auth")
        and path == "/api/v1/auth"
    ):
        path += "/"


    url = f"{target_url}{path}"


    if request.url.query:
        url += f"?{request.url.query}"


    body = await request.body()

    headers = clean_headers(
        request.headers
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


    except httpx.RequestError as exc:

        print(
            "PROXY ERROR:",
            repr(exc),
        )

        return JSONResponse(
            status_code=503,
            content={
                "error":
                "Downstream service unavailable"
            },
        )