"""
Application entry point.

Responsibilities
----------------
- Create FastAPI application
- Configure logging
- Register middleware
- Register exception handlers
- Register routers
- Health check
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import AppException
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from shared.common.responses import ErrorBody, ErrorResponse
# Import real API router
from app.api.v1.api import api_router
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.models.student import Student
from app.models.grade import Grade

# ---------------------------------------------------------
# Configure logging
# ---------------------------------------------------------

configure_logging()


# ---------------------------------------------------------
# Lifespan
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Application shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorBody(
                code=exc.error_code,
                message=exc.message,
                details=exc.details,
            )
        ).model_dump(mode="json"),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):

    status_code = exc.status_code

    # FastAPI HTTPBearer missing token
    if exc.detail == "Not authenticated":
        status_code = 403

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=ErrorBody(
                code="HTTP_ERROR",
                message=exc.detail,
            )
        ).model_dump(mode="json"),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error=ErrorBody(
                code="VALIDATION_ERROR",
                message="Request validation failed.",
                details=jsonable_encoder(exc.errors()),
            )
        ).model_dump(mode="json"),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
):

    return JSONResponse(
        status_code=409,
        content=ErrorResponse(
            error=ErrorBody(
                code="DATABASE_CONFLICT",
                message="Database integrity error.",
                details=str(exc.orig),
            )
        ).model_dump(mode="json"),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
):

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorBody(
                code="INTERNAL_SERVER_ERROR",
                message="Unexpected server error.",
            )
        ).model_dump(mode="json"),
    )
# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(api_router)


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health")
def health():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }