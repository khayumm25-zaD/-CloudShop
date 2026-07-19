"""Common dependencies for FastAPI endpoints."""

from typing import Optional
from fastapi import Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from .utils import get_db as _get_db, get_redis as _get_redis
from .security import get_current_user, TokenData


def get_db() -> Session:
    """Get database session."""
    return next(_get_db())


def get_redis():
    """Get Redis client."""
    return _get_redis()


def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        20, ge=1, le=100, description="Items per page"
    ),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query(
        "asc", regex="^(asc|desc)$", description="Sort order"
    ),
):
    """Parse pagination parameters."""
    return {
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }


def require_admin(
    current_user: TokenData = Depends(get_current_user),
):
    """Require admin role."""
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_user(
    current_user: TokenData = Depends(get_current_user),
):
    """Require authenticated user."""
    return current_user
