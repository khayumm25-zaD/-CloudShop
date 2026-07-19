"""Custom exception classes for consistent error handling."""

from typing import Any, Dict, Optional
from fastapi import status


class AppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class HTTPException(AppException):
    """Generic HTTP exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "HTTP_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, error_code, details)


class ValidationException(AppException):
    """Raised when input validation fails."""

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            details,
        )


class AuthenticationException(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED,
            "AUTHENTICATION_ERROR",
        )


class AuthorizationException(AppException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message,
            status.HTTP_403_FORBIDDEN,
            "AUTHORIZATION_ERROR",
        )


class ResourceNotFoundException(AppException):
    """Raised when requested resource is not found."""

    def __init__(self, resource: str, resource_id: Any):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
            "RESOURCE_NOT_FOUND",
        )


class ConflictException(AppException):
    """Raised when there's a resource conflict."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            status.HTTP_409_CONFLICT,
            "CONFLICT_ERROR",
            details,
        )


class RateLimitException(AppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message,
            status.HTTP_429_TOO_MANY_REQUESTS,
            "RATE_LIMIT_EXCEEDED",
        )


class ServiceUnavailableException(AppException):
    """Raised when external service is unavailable."""

    def __init__(self, service_name: str):
        message = f"{service_name} is currently unavailable"
        super().__init__(
            message,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "SERVICE_UNAVAILABLE",
        )
