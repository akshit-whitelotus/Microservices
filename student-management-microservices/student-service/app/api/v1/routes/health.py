from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import engine

router = APIRouter()


@router.get("/health")
def health():
    """
    Health endpoint.

    Verifies:
    - FastAPI is running
    - PostgreSQL is reachable
    """
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
        "service": "student-service",
    }