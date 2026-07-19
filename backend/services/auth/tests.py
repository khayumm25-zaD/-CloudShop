"""Auth Service tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.shared.models import Base
from backend.services.auth.main import app
from backend.services.auth.models import User
from backend.shared.deps import get_db

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override get_db for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestAuthService:
    """Tests for authentication service."""

    def test_register_user(self):
        """Test user registration."""
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_login_user(self):
        """Test user login."""
        # Register first
        client.post(
            "/auth/register",
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "SecurePass123!",
            },
        )

        # Login
        response = client.post(
            "/auth/login",
            json={
                "email": "test2@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_invalid_password(self):
        """Test invalid password strength."""
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser3",
                "email": "test3@example.com",
                "password": "weakpass",
            },
        )
        assert response.status_code == 422

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
