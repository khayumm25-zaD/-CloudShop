"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response."""

    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid input",
                "details": {"field": "Invalid value"},
                "timestamp": "2026-07-19T06:00:00Z",
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("asc", description="Sort order")

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "sort_by": "created_at",
                "sort_order": "desc",
            }
        }


class PaginatedResponse(BaseModel):
    """Generic paginated response."""

    data: List[Any] = Field(..., description="Data items")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total items")
    total_pages: int = Field(..., description="Total pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field("healthy", description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, str] = Field(default_factory=dict)


class ReadyResponse(BaseModel):
    """Readiness check response."""

    ready: bool = Field(..., description="Service readiness")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
