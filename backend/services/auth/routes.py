"""Auth Service API routes."""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from .schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    ChangePasswordRequest,
)
from .service import AuthService
from .repository import UserRepository
from backend.shared.deps import get_db, require_user
from backend.shared.security import TokenData
from backend.shared.utils import get_logger
from backend.shared.exceptions import (
    ValidationException,
    AuthenticationException,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user."""
    try:
        user = AuthService.register(
            db=db,
            username=request.username,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )
        return UserResponse.from_attributes(user)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return JWT token",
)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate user and return access token."""
    try:
        token, expires_in = AuthService.login(
            db=db,
            email=request.email,
            password=request.password,
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get authenticated user's profile information",
)
async def get_profile(
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get current user profile."""
    try:
        user = AuthService.get_user_profile(db, current_user.user_id)
        return UserResponse.from_attributes(user)
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile",
        )


@router.post(
    "/change-password",
    response_model=dict,
    summary="Change password",
    description="Change current user's password",
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Change user password."""
    try:
        UserRepository.change_password(
            db=db,
            user_id=current_user.user_id,
            current_password=request.current_password,
            new_password=request.new_password,
        )
        return {"message": "Password changed successfully"}
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if authentication service is healthy",
)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "auth",
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )


@router.get(
    "/ready",
    summary="Readiness check",
    description="Check if authentication service is ready to serve",
)
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check endpoint."""
    try:
        db.execute("SELECT 1")
        return {"ready": True}
    except Exception:
        return {"ready": False}
