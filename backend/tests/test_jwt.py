"""
JWT Cryptographic Engine Unit Tests.

Validates access/refresh token generation, claim deserialization,
and expiration validation.
"""

import pytest
from datetime import timedelta
from app.core.jwt import JWTEngine
from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.schemas.auth_enums import TokenType, UserRole


@pytest.fixture
def jwt_engine() -> JWTEngine:
    return JWTEngine(
        secret_key="TEST_SECRET_KEY_FOR_UNIT_TESTS",
        algorithm="HS256",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )


def test_access_token_creation_and_decoding(jwt_engine: JWTEngine) -> None:
    """Tests issuing and decoding valid Access Tokens."""
    token, payload = jwt_engine.create_access_token(
        subject="100",
        role=UserRole.PATIENT,
        permissions=["patient:read"],
        session_id="test-session-uuid",
    )

    decoded = jwt_engine.decode_token(token, expected_type=TokenType.ACCESS)
    assert decoded.sub == "100"
    assert decoded.role == UserRole.PATIENT
    assert decoded.sid == "test-session-uuid"
    assert "patient:read" in decoded.permissions


def test_refresh_token_type_mismatch(jwt_engine: JWTEngine) -> None:
    """Tests rejection when presenting a Refresh Token as an Access Token."""
    token, _ = jwt_engine.create_refresh_token(
        subject="100",
        role=UserRole.PATIENT,
        session_id="test-session-uuid",
    )

    with pytest.raises(InvalidTokenError):
        jwt_engine.decode_token(token, expected_type=TokenType.ACCESS)


def test_expired_token_rejection() -> None:
    """Tests that expired JWT tokens raise TokenExpiredError."""
    short_lived_engine = JWTEngine(
        secret_key="TEST_SECRET_KEY",
        access_token_expire_minutes=-1,  # Expired in past
    )

    token, _ = short_lived_engine.create_access_token(
        subject="100",
        role=UserRole.PATIENT,
        permissions=[],
    )

    with pytest.raises(TokenExpiredError):
        short_lived_engine.decode_token(token)