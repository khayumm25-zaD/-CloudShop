"""Auth Service application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from backend.shared.config import settings
from backend.shared.middleware import (
    CorrelationIDMiddleware,
    LoggingMiddleware,
    MetricsMiddleware,
)
from backend.shared.utils import get_logger
from .routes import router

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="CloudShop Authentication Service",
        description="JWT authentication service for CloudShop",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Add custom middleware
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MetricsMiddleware)

    # Mount Prometheus metrics
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # Include routes
    app.include_router(router)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint."""
        return {
            "service": "Authentication Service",
            "version": "1.0.0",
            "docs": "/docs",
        }

    # Exception handlers
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    logger.info("Auth service initialized")
    return app


app = create_app()
