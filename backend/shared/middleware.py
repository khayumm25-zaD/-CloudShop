"""ASGI middleware for cross-cutting concerns."""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram

from .utils import get_logger, create_correlation_id

logger = get_logger(__name__)

# Prometheus metrics
request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Add correlation ID to all requests and responses."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        correlation_id = request.headers.get(
            "x-correlation-id", create_correlation_id()
        )
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests and responses."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        correlation_id = getattr(
            request.state, "correlation_id", create_correlation_id()
        )

        extra_data = {
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        }
        logger.info(f"Request started", extra=extra_data)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        extra_data["status_code"] = response.status_code
        extra_data["duration_ms"] = int(duration * 1000)
        logger.info(f"Request completed", extra=extra_data)

        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect Prometheus metrics for all requests."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()

        request_duration.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)

        return response
