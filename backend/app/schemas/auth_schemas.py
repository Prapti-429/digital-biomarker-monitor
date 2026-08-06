"""
Authentication Data Transfer Objects (DTOs).

Defines input validation schemas and response contracts for registration,
login, token lifecycle, password management, and email verification workflows.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import validate_password_complexity
from app.schemas.auth_enums import UserRole


# =============================================================================
# AUTHENTICATION REQUEST SCHEMAS
# =============================================================================

class UserRegisterRequest(BaseModel):
    """Payload for new user self-registration."""
    email: EmailStr = Field(..., description="Unique user email address", example="patient@example.com")
    password: str = Field(..., min_length=12, max_length=128, description="Raw candidate password")
    full_name: Optional[str] = Field(None, max_length=255, description="User full legal or display name")
    role: UserRole = Field(default=UserRole.PATIENT, description="Requested user role")

    @field_validator("password")
    @classmethod
    def check_password_policy(cls, v: str) -> str:
        """Enforces NIST SP 800-63B password complexity requirements."""
        validate_password_complexity(v)
        return v


class LoginRequest(BaseModel):
    """Payload for password-based user authentication."""
    email: EmailStr = Field(..., description="Registered user email", example="patient@example.com")
    password: str = Field(..., description="User password")
    device_fingerprint: Optional[str] = Field(None, max_length=255, description="Client device fingerprint")


class RefreshTokenRequest(BaseModel):
    """Payload for acquiring a new Access/Refresh token pair."""
    refresh_token: str = Field(..., description="Valid, unexpired JWT Refresh Token string")


class ForgotPasswordRequest(BaseModel):
    """Payload to initiate a self-service password reset email."""
    email: EmailStr = Field(..., description="Registered account email address")


class ResetPasswordRequest(BaseModel):
    """Payload to execute password replacement via reset token."""
    token: str = Field(..., description="Single-use password reset token string")
    new_password: str = Field(..., min_length=12, max_length=128, description="New candidate password")

    @field_validator("new_password")
    @classmethod
    def check_new_password_policy(cls, v: str) -> str:
        validate_password_complexity(v)
        return v


class ChangePasswordRequest(BaseModel):
    """Payload for authenticated users to update their password."""
    current_password: str = Field(..., description="Existing active password")
    new_password: str = Field(..., min_length=12, max_length=128, description="Replacement password")

    @field_validator("new_password")
    @classmethod
    def check_change_password_policy(cls, v: str) -> str:
        validate_password_complexity(v)
        return v


class VerifyEmailRequest(BaseModel):
    """Payload to confirm email address ownership."""
    token: str = Field(..., description="Single-use email verification token")


# =============================================================================
# AUTHENTICATION RESPONSE SCHEMAS
# =============================================================================

class TokenResponse(BaseModel):
    """JWT Token pair returned upon successful login or refresh."""
    access_token: str = Field(..., description="Short-lived JWT Access Token")
    refresh_token: str = Field(..., description="Long-lived JWT Refresh Token")
    token_type: str = Field(default="Bearer", description="OAuth2 Token Type")
    expires_in: int = Field(..., description="Access token lifetime in seconds")


class UserSessionResponse(BaseModel):
    """Public details for an active user session."""
    id: str = Field(..., description="Session unique identifier")
    ip_address: Optional[str] = Field(None, description="IP address associated with login")
    user_agent: Optional[str] = Field(None, description="Client user agent string")
    is_revoked: bool = Field(..., description="Revocation state flag")
    created_at: datetime = Field(..., description="Session establishment UTC timestamp")
    last_activity_at: datetime = Field(..., description="Last recorded activity UTC timestamp")
    expires_at: datetime = Field(..., description="Session expiration UTC timestamp")

    model_config = ConfigDict(from_attributes=True)