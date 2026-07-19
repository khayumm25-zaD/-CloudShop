"""Shared utilities and libraries for all microservices."""

from .config import settings
from .models import Base
from .schemas import ErrorResponse
from .utils import get_db, get_redis, get_logger, create_correlation_id
from .exceptions import (
    HTTPException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    ConflictException,
    RateLimitException,
    ServiceUnavailableException,
)

__all__ = [
    "settings",
    "Base",
    "ErrorResponse",
    "get_db",
    "get_redis",
    "get_logger",
    "create_correlation_id",
    "HTTPException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "ConflictException",
    "RateLimitException",
    "ServiceUnavailableException",
]
