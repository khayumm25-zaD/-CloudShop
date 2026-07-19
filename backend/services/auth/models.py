"""Authentication Service - User registration, login, and JWT token management."""

from sqlalchemy import Column, String, Boolean, DateTime, Index
from datetime import datetime
from backend.shared.models import BaseModel


class User(BaseModel):
    """User model for authentication."""

    __tablename__ = "users"
    __table_args__ = (
        Index("idx_email", "email", unique=True),
        Index("idx_username", "username", unique=True),
    )

    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(120), nullable=False, unique=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
