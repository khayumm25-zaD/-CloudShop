"""Utility functions and dependencies."""

import logging
import uuid
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from redis import Redis, ConnectionPool
from pythonjsonlogger import jsonlogger

from .config import settings

# Database setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# Redis setup
redis_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=50,
    socket_keepalive=True,
)
redis_client = Redis(connection_pool=redis_pool, decode_responses=True)


def get_db() -> Generator[Session, None, None]:
    """Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> Redis:
    """Dependency for Redis client."""
    return redis_client


def get_logger(name: str) -> logging.Logger:
    """Get configured logger with JSON formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def create_correlation_id() -> str:
    """Create a unique correlation ID for request tracing."""
    return str(uuid.uuid4())
