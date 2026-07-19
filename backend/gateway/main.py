"""API Gateway - Central entry point for all microservices."""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from httpx import AsyncClient, ConnectError, TimeoutException
import os
from typing import Optional

from backend.shared.config import settings
from backend.shared.middleware import (
    CorrelationIDMiddleware,
    LoggingMiddleware,
    MetricsMiddleware,
    RateLimitMiddleware,
)
from backend.shared.utils import get_logger
from prometheus_client import make_asgi_app

logger = get_logger(__name__)

# Service URLs
SERVICE_URLS = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
    "user": os.getenv("USER_SERVICE_URL", "http://localhost:8002"),
    "product": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003"),
    "cart": os.getenv("CART_SERVICE_URL", "http://localhost:8004"),
    "order": os.getenv("ORDER_SERVICE_URL", "http://localhost:8005"),
    "payment": os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8006"),
}


class APIGateway:
    """API Gateway for routing requests to microservices."""

    def __init__(self):
        self.app = FastAPI(
            title="CloudShop API Gateway",
            description="Central entry point for CloudShop microservices",
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
            openapi_url="/api/openapi.json",
        )
        self.setup_middleware()
        self.setup_routes()
        self.client = None

    def setup_middleware(self):
        """Setup middleware."""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        )

        # Custom middleware
        self.app.add_middleware(RateLimitMiddleware)
        self.app.add_middleware(CorrelationIDMiddleware)
        self.app.add_middleware(LoggingMiddleware)
        self.app.add_middleware(MetricsMiddleware)

        # Prometheus metrics
        metrics_app = make_asgi_app()
        self.app.mount("/metrics", metrics_app)

    def setup_routes(self):
        """Setup API routes."""
        # Root endpoint
        @self.app.get("/", tags=["gateway"])
        async def root():
            return {
                "service": "API Gateway",
                "version": "1.0.0",
                "status": "running",
            }

        # Health check
        @self.app.get("/health", tags=["gateway"])
        async def health_check():
            services_status = {}
            async with AsyncClient(timeout=5.0) as client:
                for service_name, url in SERVICE_URLS.items():
                    try:
                        response = await client.get(f"{url}/health")
                        services_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
                    except Exception:
                        services_status[service_name] = "unhealthy"

            return {
                "status": "healthy",
                "gateway": "running",
                "services": services_status,
            }

        # Service status
        @self.app.get("/status", tags=["gateway"])
        async def service_status():
            return {
                "services": SERVICE_URLS,
                "gateway_version": "1.0.0",
            }

        # Route handlers
        @self.app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def gateway_route(request: Request, service: str, path: str):
            return await self.route_request(request, service, path)

    async def route_request(self, request: Request, service: str, path: str):
        """Route request to appropriate microservice."""
        # Validate service
        if service not in SERVICE_URLS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service}' not found",
            )

        service_url = SERVICE_URLS[service]
        url = f"{service_url}/{path}"

        # Build headers
        headers = {}
        for header, value in request.headers.items():
            if header.lower() not in ["host", "connection"]:
                headers[header] = value

        # Add correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        # Get request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

        try:
            async with AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers=headers,
                    content=body,
                    params=request.query_params,
                )

                return JSONResponse(
                    status_code=response.status_code,
                    content=response.json() if response.text else {},
                )

        except ConnectError:
            logger.error(f"Failed to connect to {service} service at {service_url}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service '{service}' is unavailable",
            )
        except TimeoutException:
            logger.error(f"Request to {service} service timed out")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Service '{service}' request timed out",
            )
        except Exception as e:
            logger.error(f"Error routing request to {service}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal gateway error",
            )


def create_app() -> FastAPI:
    """Create and configure API Gateway."""
    gateway = APIGateway()
    logger.info("API Gateway initialized")
    return gateway.app


app = create_app()
