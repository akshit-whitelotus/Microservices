from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    AUTH_SERVICE_URL: str

    STUDENT_SERVICE_URL: str

    REQUEST_TIMEOUT_SECONDS: float = 5


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()