"""Auth Service schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
            }
        }


class UserLoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")

    class Config:
        schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "SecurePass123!",
            }
        }


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
            }
        }


class UserResponse(BaseModel):
    """User response model."""

    id: str
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": True,
                "is_admin": False,
                "created_at": "2026-07-19T06:00:00Z",
            }
        }


class ChangePasswordRequest(BaseModel):
    """Change password request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @validator("new_password")
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Verify passwords match."""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v
