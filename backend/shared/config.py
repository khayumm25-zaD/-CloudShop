"""Configuration management using environment variables (12-Factor App)."""

import os
from typing import Optional
from functools import lru_cache


class Settings:
    """Application settings from environment variables."""

    # Application
    APP_NAME = os.getenv("APP_NAME", "CloudShop-Microservice")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    WORKERS = int(os.getenv("WORKERS", "4"))

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/cloudshop",
    )
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
    DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", "3600"))
    REDIS_SESSION_TTL = int(os.getenv("REDIS_SESSION_TTL", "86400"))

    # JWT
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY", "your-secret-key-change-in-production"
    )
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # RabbitMQ
    RABBITMQ_URL = os.getenv(
        "RABBITMQ_URL", "amqp://guest:guest@localhost:5672//"
    )
    RABBITMQ_PREFETCH_COUNT = int(os.getenv("RABBITMQ_PREFETCH_COUNT", "10"))

    # CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

    # Monitoring
    METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))

    # External Services
    GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:8000")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8001")
    PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product:8002")
    CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://cart:8003")
    ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order:8004")
    PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment:8005")
    INVENTORY_SERVICE_URL = os.getenv(
        "INVENTORY_SERVICE_URL", "http://inventory:8006"
    )
    NOTIFICATION_SERVICE_URL = os.getenv(
        "NOTIFICATION_SERVICE_URL", "http://notification:8007"
    )

    # Email
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "your-email@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-password")
    SMTP_FROM = os.getenv("SMTP_FROM", "noreply@cloudshop.com")

    # GCP
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "cloudshop-prod")
    GCP_REGION = os.getenv("GCP_REGION", "us-central1")

    # Feature Flags
    FEATURE_PAYMENT_ENABLED = (
        os.getenv("FEATURE_PAYMENT_ENABLED", "true").lower() == "true"
    )
    FEATURE_REVIEWS_ENABLED = (
        os.getenv("FEATURE_REVIEWS_ENABLED", "true").lower() == "true"
    )
    FEATURE_RECOMMENDATIONS_ENABLED = (
        os.getenv("FEATURE_RECOMMENDATIONS_ENABLED", "true").lower() == "true"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
