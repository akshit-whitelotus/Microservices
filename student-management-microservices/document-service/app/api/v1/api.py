from fastapi import APIRouter

from app.api.v1.routes import documents
from app.api.v1.routes import health


api_router = APIRouter()


api_router.include_router(
    documents.router
)


api_router.include_router(
    health.router
)