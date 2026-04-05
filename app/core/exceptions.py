from typing import Any, Dict, Optional
from fastapi import status


class AppException(Exception):
    """
    Base class for all custom application exceptions.
    """
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "An unexpected error occurred"
    code: str = "INTERNAL_SERVER_ERROR"

    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message or self.message)
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        self.code = code or self.code
        self.details = details or {}


class ObjectNotFoundError(AppException):
    """
    Exception raised when a requested resource is not found.
    """
    status_code = status.HTTP_404_NOT_FOUND
    message = "Resource not found"
    code = "NOT_FOUND"


class DuplicateError(AppException):
    """
    Exception raised when a resource duplication is attempted (e.g., unique constraint).
    """
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Resource already exists"
    code = "DUPLICATE_ERROR"


class CredentialsError(AppException):
    """
    Exception raised for authentication-related failures.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid credentials"
    code = "INVALID_CREDENTIALS"


class ForbiddenError(AppException):
    """
    Exception raised for authorization-related failures.
    """
    status_code = status.HTTP_403_FORBIDDEN
    message = "Access forbidden"
    code = "ACCESS_FORBIDDEN"


class ValidationError(AppException):
    """
    Exception raised for validation errors.
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    message = "Validation error"
    code = "VALIDATION_ERROR"
