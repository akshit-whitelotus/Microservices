from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html

import httpx
from app.core.config import settings
from app.proxy import proxy_request
from app.openapi_merge import merged_openapi

app=FastAPI(
    title="Unified Gateway API",
    docs_url=None,
    openapi_url=None
)

@app.get("/openapi.json")
async def openapi():
    spec=await merged_openapi(settings.AUTH_SERVICE_URL,settings.STUDENT_SERVICE_URL)
    return spec

@app.get("/docs")
async def docs():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Gateway Docs"
    )

@app.api_route("/api/v1/auth/{path:path}",methods=["GET","POST","DELETE","PUT"])
async def auth_proxy(request:Request,path:str):
    print("AUTH_SERVICE_URL =", settings.AUTH_SERVICE_URL)
    return await proxy_request(request,settings.AUTH_SERVICE_URL)

@app.api_route("/api/v1/students/{path:path}",methods=["GET","POST","DELETE","PUT"])
async def auth_proxy(request:Request,path:str):
    return await proxy_request(request,settings.STUDENT_SERVICE_URL)

@app.get("/health")
async def health():
    services={}
    overall="healthy"
    checks={
        "auth":(
            settings.AUTH_SERVICE_URL +"/api/v1/health"
        ),
        "students":(
            settings.STUDENT_SERVICE_URL +"/health"
        )
    }
    async with httpx.AsyncClient(timeout=settings.REQUETS_TIMEOUT_SECONDS)as client:
        for name ,url in checks.items():
            try:
                response=await client.get(url)
                services[name] = {
                    "status":"healthy",
                    "status_code":response.status_code,
                    "body":response.json()
                }
            except Exception:
                overall="degraded"
                services[name]={
                    "status":"unreachable"
                }
        return {
            "gateway":"healthy",
            "overall":overall,
            "services":services
        }
    


