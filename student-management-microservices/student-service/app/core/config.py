"""
Application configuration.

Responsibilities
----------------
- Load configuration from .env
- Provide a singleton Settings instance
- No other file should read environment variables directly.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from shared.auth.constants import (
    JWT_ISSUER,
    JWT_AUDIENCE,
    API_V1_PREFIX,
)


class Settings(BaseSettings):
    """
    Student Service settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    APP_NAME: str = "Student Service"

    APP_VERSION: str = "1.0.0"

    API_V1_PREFIX: str = API_V1_PREFIX

    DEBUG: bool = True

    LOG_LEVEL: str = "INFO"

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------

    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database URL",
    )

    # ---------------------------------------------------------
    # Auth Service
    # ---------------------------------------------------------

    AUTH_SERVICE_URL: str = "http://localhost:8000"

    # ---------------------------------------------------------
    # JWT
    # ---------------------------------------------------------

    JWT_SECRET_KEY: str = Field(
        ...,
        min_length=32,
    )

    JWT_ALGORITHM: str = "HS256"

    JWT_ISSUER: str = JWT_ISSUER

    JWT_AUDIENCE: str = JWT_AUDIENCE

    # ---------------------------------------------------------
    # Pagination
    # ---------------------------------------------------------

    DEFAULT_PAGE_SIZE: int = 10

    MAX_PAGE_SIZE: int = 100

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(
        cls,
        value: str,
    ) -> str:

        allowed = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        value = value.upper()

        if value not in allowed:
            raise ValueError(
                f"Invalid LOG_LEVEL: {value}"
            )

        return value


@lru_cache
def get_settings() -> Settings:
    """
    Return cached settings.
    """
    return Settings()


settings = get_settings()