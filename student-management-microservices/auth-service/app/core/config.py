from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.auth.constants import (
    JWT_ISSUER,
    JWT_AUDIENCE,
    API_V1_PREFIX,
)

class Settings(BaseSettings):
    APP_NAME: str = "Auth Service"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Standard JWT Claims
    JWT_ISSUER: str = JWT_ISSUER
    JWT_AUDIENCE: str = JWT_AUDIENCE
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()