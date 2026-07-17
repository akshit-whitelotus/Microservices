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
    API_V1_PREFIX,
)


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    APP_NAME: str = "Document Service"

    APP_VERSION: str = "1.0.0"

    API_V1_PREFIX: str = API_V1_PREFIX

    DATABASE_URL: str

    JWT_SECRET_KEY: str

    JWT_ALGORITHM: str = "HS256"

    JWT_ISSUER: str = JWT_ISSUER

    JWT_AUDIENCE: str = JWT_AUDIENCE

    AI_API_URL: str

    AI_API_KEY: str

    STUDENT_SERVICE_URL: str

    INTERNAL_SERVICE_TOKEN: str

    UPLOAD_DIR: str = "uploads"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()