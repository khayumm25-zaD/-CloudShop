"""Security utilities for JWT and authentication."""

from datetime import datetime, timedelta
from typing import Optional, List
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel

from .config import settings
from .utils import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str
    email: str
    roles: List[str] = []
    exp: datetime
    iat: datetime


class TokenData(BaseModel):
    """Token data for dependency."""

    user_id: str
    email: str
    roles: List[str] = []


class SecurityUtils:
    """Security utilities for JWT operations."""

    @staticmethod
    def create_access_token(
        user_id: str,
        email: str,
        roles: List[str] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(
                hours=settings.JWT_EXPIRATION_HOURS
            )

        expires = datetime.utcnow() + expires_delta
        payload = {
            "sub": user_id,
            "email": email,
            "roles": roles or [],
            "exp": expires,
            "iat": datetime.utcnow(),
        }

        encoded_jwt = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> TokenPayload:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> TokenData:
    """Get current authenticated user from token."""
    token = SecurityUtils.verify_token(credentials.credentials)
    return TokenData(
        user_id=token.sub,
        email=token.email,
        roles=token.roles,
    )
