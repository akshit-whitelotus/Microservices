from fastapi import Request
from fastapi.responses import Response,JSONResponse
import httpx
from app.core.config import settings

HOP_BY_HOP_HEADERS={
    "connection",
    "host",
    "transfer-encoding",
    "content-length"
}

def clean_headers(headers):
    return {
        k:v
        for k,v in headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS
    }
async def proxy_request(request:Request,target_url:str):
    path=request.url.path
    query=request.url.query

    url=f"{target_url}{path}"
    if query:
        url +=f"?{query}"
    body=await request.body()
    headers=clean_headers(request.headers)
    try:
        async with httpx.AsyncClient(timeout=settings.REQUETS_TIMEOUT_SECONDS) as client:
            print(f"Forwarding {request.method} -> {url}")
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body
            )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=clean_headers(response.headers),
            media_type=response.headers.get("content-type"),
        )
    except httpx.RequestError:
        return JSONResponse(
            status_code=503,
            content={
                "error":"Downstream service unavailable"
            }
        )
    