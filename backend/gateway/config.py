"""Gateway service configuration and utilities."""

from typing import Dict, List
import os


class GatewayConfig:
    """Gateway configuration."""

    # Service routes
    SERVICE_ROUTES: Dict[str, Dict[str, str]] = {
        "auth": {
            "url": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
            "timeout": 10,
            "retry": 3,
        },
        "user": {
            "url": os.getenv("USER_SERVICE_URL", "http://localhost:8002"),
            "timeout": 10,
            "retry": 3,
        },
        "product": {
            "url": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003"),
            "timeout": 10,
            "retry": 3,
        },
        "cart": {
            "url": os.getenv("CART_SERVICE_URL", "http://localhost:8004"),
            "timeout": 10,
            "retry": 3,
        },
        "order": {
            "url": os.getenv("ORDER_SERVICE_URL", "http://localhost:8005"),
            "timeout": 15,
            "retry": 3,
        },
        "payment": {
            "url": os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8006"),
            "timeout": 20,
            "retry": 5,
        },
    }

    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds

    # Request/Response
    MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds
    ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"

    # Caching
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # seconds


class CircuitBreaker:
    """Circuit breaker for service resilience."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def record_success(self):
        """Record successful request."""
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self):
        """Record failed request."""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            from datetime import datetime
            self.last_failure_time = datetime.utcnow()

    def is_available(self) -> bool:
        """Check if service is available."""
        if self.state == "closed":
            return True
        elif self.state == "open":
            from datetime import datetime, timedelta
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = "half_open"
                return True
            return False
        return self.state == "half_open"
