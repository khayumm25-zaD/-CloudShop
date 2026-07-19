"""Request/Response interceptors for API Gateway."""

from typing import Callable, Any
from functools import wraps
import json
from datetime import datetime

from backend.shared.utils import get_logger

logger = get_logger(__name__)


class RequestInterceptor:
    """Intercept and process requests before routing."""

    @staticmethod
    def validate_request(request_data: dict) -> bool:
        """Validate incoming request."""
        # Add custom validation logic
        return True

    @staticmethod
    def enrich_request(request_data: dict, context: dict) -> dict:
        """Enrich request with additional context."""
        request_data["timestamp"] = datetime.utcnow().isoformat()
        request_data["correlation_id"] = context.get("correlation_id")
        return request_data

    @staticmethod
    def log_request(method: str, path: str, data: Any) -> None:
        """Log incoming request."""
        logger.info(f"Incoming request: {method} {path}")
        if isinstance(data, dict):
            logger.debug(f"Request data: {json.dumps(data, default=str)}")


class ResponseInterceptor:
    """Intercept and process responses before sending to client."""

    @staticmethod
    def transform_response(response_data: dict, status_code: int) -> dict:
        """Transform response format."""
        return {
            "success": 200 <= status_code < 300,
            "status_code": status_code,
            "data": response_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def handle_error(error: Exception, status_code: int) -> dict:
        """Handle error responses."""
        logger.error(f"Error occurred: {str(error)}")
        return {
            "success": False,
            "status_code": status_code,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def log_response(status_code: int, response_data: Any) -> None:
        """Log outgoing response."""
        logger.info(f"Outgoing response: {status_code}")
        if isinstance(response_data, dict):
            logger.debug(f"Response data: {json.dumps(response_data, default=str)}")
