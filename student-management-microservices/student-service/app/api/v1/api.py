from fastapi import APIRouter

from app.api.v1.routes import health, students,grades

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["Health"],
)

api_router.include_router(
    students.router,
)
api_router.include_router(
    grades.router
)