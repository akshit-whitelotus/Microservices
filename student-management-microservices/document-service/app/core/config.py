from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from shared.auth.constants import (
    JWT_ISSUER,
    JWT_AUDIENCE,
)


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


    # -------------------------------------------------
    # Application
    # -------------------------------------------------

    APP_NAME: str = "Document Service"

    APP_VERSION: str = "1.0.0"

    LOG_LEVEL: str = "INFO"


    # -------------------------------------------------
    # Database
    # -------------------------------------------------

    DATABASE_URL: str 


    # -------------------------------------------------
    # JWT
    # -------------------------------------------------

    JWT_SECRET_KEY: str = Field(
        ...,
        min_length=32,
    )

    JWT_ALGORITHM: str = "HS256"

    JWT_ISSUER: str = JWT_ISSUER

    JWT_AUDIENCE: str = JWT_AUDIENCE


    # -------------------------------------------------
    # AI
    # -------------------------------------------------

    AI_API_URL: str

    AI_API_KEY: str


    # -------------------------------------------------
    # Student Service
    # -------------------------------------------------

    STUDENT_SERVICE_URL: str = (
        "http://localhost:8001"
    )


    # -------------------------------------------------
    # Internal Authentication
    # -------------------------------------------------

    INTERNAL_SERVICE_TOKEN: str


    # -------------------------------------------------
    # Storage
    # -------------------------------------------------

    UPLOAD_DIR: str = "./uploads"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()