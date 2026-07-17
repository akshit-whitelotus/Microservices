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


from fastapi import (
    FastAPI,
    Request,
    HTTPException,
)

from fastapi.exceptions import (
    RequestValidationError,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from fastapi.responses import (
    JSONResponse,
)

from fastapi.encoders import (
    jsonable_encoder,
)

from sqlalchemy import text
from sqlalchemy.exc import (
    IntegrityError,
)


from app.core.config import (
    settings,
)

from app.core.database import (
    engine,
)

from app.core.exceptions import (
    AppException,
)

from app.core.logging import (
    configure_logging,
)

from app.core.middleware import (
    RequestLoggingMiddleware,
)


from app.api.v1.api import (
    api_router,
)


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

configure_logging()



# ---------------------------------------------------------
# Lifespan
# ---------------------------------------------------------

async def lifespan(app: FastAPI):

    """
    Application lifecycle.

    Database migrations are managed by Alembic.

    Run:

        alembic upgrade head

    before starting this service.
    """

    yield



# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)



# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

app.add_middleware(
    RequestLoggingMiddleware,
)


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
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )



@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": None,
            }
        },
    )



@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": (
                    "Request validation failed."
                ),
                "details": jsonable_encoder(
                    exc.errors()
                ),
            }
        },
    )



@app.exception_handler(
    IntegrityError
)
async def integrity_exception_handler(
    request: Request,
    exc: IntegrityError,
):

    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": (
                    "DATABASE_CONFLICT"
                ),
                "message": (
                    "Database integrity error."
                ),
                "details": None,
            }
        },
    )



@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
):

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": (
                    "INTERNAL_SERVER_ERROR"
                ),
                "message": (
                    "Unexpected server error."
                ),
                "details": None,
            }
        },
    )



# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(
    api_router,
    prefix="/api/v1",
)



# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
def health():

    with engine.connect() as connection:

        connection.execute(
            text("SELECT 1")
        )


    return {
        "status": "healthy",
        "database": "connected",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }



@app.get("/")
def root():

    return {
        "message": (
            "Document Service Running"
        )
    }