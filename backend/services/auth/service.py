"""Auth Service business logic."""

from typing import Tuple
from sqlalchemy.orm import Session
from datetime import timedelta

from .models import User
from .repository import UserRepository
from backend.shared.security import SecurityUtils
from backend.shared.exceptions import AuthenticationException
from backend.shared.config import settings
from backend.shared.utils import get_logger

logger = get_logger(__name__)


class AuthService:
    """Business logic for authentication."""

    @staticmethod
    def register(
        db: Session,
        username: str,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
    ) -> User:
        """Register a new user."""
        user = UserRepository.create_user(
            db=db,
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        logger.info(f"User registered: {user.email}")
        return user

    @staticmethod
    def login(db: Session, email: str, password: str) -> Tuple[str, int]:
        """Authenticate user and return access token.
        
        Returns:
            Tuple of (access_token, expires_in_seconds)
        """
        # Get user
        user = UserRepository.get_user_by_email(db, email)
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise AuthenticationException("Invalid email or password")

        # Verify password
        if not UserRepository.verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {email}")
            raise AuthenticationException("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            raise AuthenticationException("User account is inactive")

        # Update last login
        UserRepository.update_last_login(db, user.id)

        # Generate token
        roles = ["admin"] if user.is_admin else ["user"]
        token = SecurityUtils.create_access_token(
            user_id=user.id,
            email=user.email,
            roles=roles,
            expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        )

        expires_in = settings.JWT_EXPIRATION_HOURS * 3600
        logger.info(f"User logged in: {user.email}")
        return token, expires_in

    @staticmethod
    def get_user_profile(db: Session, user_id: str) -> User:
        """Get user profile."""
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise AuthenticationException("User not found")
        return user
