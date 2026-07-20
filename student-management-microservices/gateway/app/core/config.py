from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    AUTH_SERVICE_URL: str

    STUDENT_SERVICE_URL: str

    DOCUMENT_SERVICE_URL: str
    AI_SERVICE_URL:str


    REQUEST_TIMEOUT_SECONDS: float = 5


    INTERNAL_SERVICE_SECRET: str


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()