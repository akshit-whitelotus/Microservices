from fastapi import Header
from app.core.config import settings
from app.core.exceptions import UnauthorizedException

def verify_internal_service(
    x_internal_service_token: str | None = Header(
        default=None,
        alias="X-Internal-Service-Token",
    ),
) -> None:
    if x_internal_service_token != settings.INTERNAL_SERVICE_TOKEN:
        raise UnauthorizedException(message="Invalid internal service token")
