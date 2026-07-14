from fastapi import FastAPI

from app.database import Base, engine
from app.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="Microservice responsible for managing users."
)

# Include API routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "User Service",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "Healthy"
    }