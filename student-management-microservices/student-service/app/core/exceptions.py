from __future__ import annotations


class AppException(Exception):
    """
    Base application exception.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: str,
        details=None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

        super().__init__(message)



class NotFoundException(AppException):
    def __init__(
        self,
        message: str = "Resource not found.",
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
        )



class ConflictException(AppException):
    def __init__(
        self,
        message: str = "Conflict.",
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
        )



class BadRequestException(AppException):
    def __init__(
        self,
        message: str = "Bad request.",
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
        )