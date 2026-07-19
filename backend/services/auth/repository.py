"""Auth Service repository for database operations."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext

from .models import User
from backend.shared.exceptions import ResourceNotFoundException, ConflictException
from backend.shared.utils import get_logger

logger = get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    """Repository for User database operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        # Check if user already exists
        existing = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing:
            raise ConflictException(
                message="Username or email already exists",
                details={"field": "username" if existing.username == username else "email"},
            )

        # Create new user
        user = User(
            username=username,
            email=email,
            hashed_password=UserRepository.hash_password(password),
            first_name=first_name,
            last_name=last_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created: {user.id}")
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_last_login(db: Session, user_id: str) -> User:
        """Update user's last login timestamp."""
        from datetime import datetime
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> User:
        """Change user password."""
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)

        # Verify current password
        if not UserRepository.verify_password(current_password, user.hashed_password):
            from backend.shared.exceptions import AuthenticationException
            raise AuthenticationException("Current password is incorrect")

        # Update password
        user.hashed_password = UserRepository.hash_password(new_password)
        db.commit()
        db.refresh(user)
        logger.info(f"Password changed for user: {user_id}")
        return user
