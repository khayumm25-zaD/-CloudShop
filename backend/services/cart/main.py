"""Cart Service application factory."""

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
from .routes import router, wishlist_router

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="CloudShop Cart Service",
        description="Shopping cart and wishlist service",
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
    app.include_router(wishlist_router)

    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint."""
        return {
            "service": "Cart Service",
            "version": "1.0.0",
            "docs": "/docs",
        }

    logger.info("Cart service initialized")
    return app


app = create_app()
