from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.v1.api import api_router
from shared.common.responses import ErrorBody, ErrorResponse



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)


# ---------------------------------------------------------
# Exception Handlers
#
# Same {"error": {code, message, details}} envelope as
# student-service and document-service (shared/common/responses.py),
# so API consumers see one consistent error shape across the whole
# platform instead of auth-service falling back to FastAPI's raw
# {"detail": ...} default.
# ---------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
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


@app.get("/")
async def root():
    return {
        "message": "Auth Service Running"
    }