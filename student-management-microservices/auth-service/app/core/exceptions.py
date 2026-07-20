from __future__ import annotations
from typing import Any
class AppException(Exception):
    def __init__(self,*,message: str,status_code: int,error_code: str,details: Any | None = None,) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)
class BadRequestException(AppException):
    def __init__(self,message: str = "Bad request.",details: Any | None = None,) -> None:
        super().__init__( message=message,status_code=400,error_code="BAD_REQUEST",details=details,)
class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized.",details: Any | None = None,) -> None:
        super().__init__(message=message,status_code=401,error_code="UNAUTHORIZED",details=details,)
class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden.",details: Any | None = None,) -> None:
        super().__init__(message=message,status_code=403,error_code="FORBIDDEN",details=details,)
class NotFoundException(AppException):
    def __init__( self, message: str = "Resource not found.",details: Any | None = None,) -> None:
        super().__init__(message=message,status_code=404,error_code="NOT_FOUND",details=details,)
class ConflictException(AppException):
    def __init__(self,message: str = "Resource already exists.",details: Any | None = None,) -> None:
        super().__init__(message=message,status_code=409,error_code="CONFLICT",details=details,)
class InternalServerException(AppException):
    def __init__(self,message: str = "Internal server error.",details: Any | None = None,) -> None:
        super().__init__( message=message,status_code=500,error_code="INTERNAL_SERVER_ERROR",details=details,)