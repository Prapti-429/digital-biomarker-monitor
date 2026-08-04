"""
API Endpoint Integration Tests.

Validates application HTTP endpoints, router behavior, and database health check responses.
"""

from fastapi.testclient import TestClient
import pytest

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """
    Verifies that the root endpoint returns correct project metadata.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION


def test_health_check_endpoint():
    """
    Verifies that the health endpoint executes active database connectivity probes
    and returns expected telemetry JSON structures.
    """
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "project_name" in data
    assert "database" in data
    
    db_info = data["database"]
    assert db_info["database"] == "postgresql"
    assert "latency_ms" in db_info
    assert db_info["status"] in ["healthy", "unhealthy"]


def test_security_headers_middleware():
    """
    Verifies that response headers contain required security enforcement values.
    """
    response = client.get(f"{settings.API_V1_STR}/health")
    headers = response.headers
    
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"