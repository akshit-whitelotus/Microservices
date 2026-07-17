from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router



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


@app.get("/")
async def root():
    return {
        "message": "Auth Service Running"
    }