"""
Authentication and Authorization API Integration Tests.

Validates registration, authentication workflows, lockout thresholds,
token rotation, and RBAC access boundaries.
"""

from fastapi import status
from fastapi.testclient import TestClient
from app.db.models import User


def test_user_registration_success(client: TestClient) -> None:
    """Tests successful user registration via API endpoint."""
    payload = {
        "email": "newpatient@example.com",
        "password": "StrongP@ssw0rd2026!",
        "full_name": "New Patient",
        "role": "patient",
    }

    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newpatient@example.com"
    assert "hashed_password" not in data


def test_user_login_success(client: TestClient, test_patient_user: User) -> None:
    """Tests successful authentication and token receipt."""
    payload = {
        "email": "patient@example.com",
        "password": "SecurePassword123!",
    }

    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


def test_user_login_invalid_credentials(client: TestClient, test_patient_user: User) -> None:
    """Tests authentication failure with invalid password."""
    payload = {
        "email": "patient@example.com",
        "password": "WrongPassword123!",
    }

    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_account_lockout_after_max_failed_attempts(client: TestClient, test_patient_user: User) -> None:
    """Tests account lockout after 5 consecutive failed login attempts."""
    payload = {
        "email": "patient@example.com",
        "password": "WrongPassword123!",
    }

    # Execute 5 failed login attempts
    for _ in range(5):
        response = client.post("/api/v1/auth/login", json=payload)

    # 6th attempt should return HTTP 423 Locked
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_423_LOCKED


def test_rbac_admin_endpoint_forbidden_for_patient(client: TestClient, test_patient_user: User) -> None:
    """Tests that patient account is forbidden from hitting admin endpoints."""
    # Login as patient
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "patient@example.com", "password": "SecurePassword123!"},
    )
    token = login_resp.json()["access_token"]

    # Attempt to query admin users list
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDENP