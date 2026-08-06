"""
Core Application Exception Classes.

Provides standardized custom exceptions for infrastructure operations including database failures.
"""

from typing import Any, Dict, Optional


class AppBaseException(Exception):
    """
    Base exception class for all custom application errors.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DatabaseException(AppBaseException):
    """
    Raised when an operational database error occurs.
    """

    pass


class DatabaseConnectionError(DatabaseException):
    """
    Raised when unable to connect to the PostgreSQL database server.
    """

    pass


class DatabaseInitializationError(DatabaseException):
    """
    Raised when database initialization or metadata binding fails.
    """

    pass


class RecordNotFoundError(DatabaseException):
    """
    Raised when a requested database record is missing.
    """

    pass

"""
Domain Security and Authentication Exception Hierarchy.

Provides domain-specific exceptions to eliminate silent failures and expose
structured, security-conscious error states without leaking sensitive telemetry.
"""

from typing import Any, Dict, Optional


class AuthBaseException(Exception):
    """Base exception for all identity and authorization failures."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidCredentialsException(AuthBaseException):
    """Raised when authentication fails due to mismatched user/password."""
    def __init__(self, message: str = "Invalid credentials provided.") -> None:
        super().__init__(message)


class TokenExpiredError(AuthBaseException):
    """Raised when a JWT access or refresh token has exceeded its lifespan."""
    def __init__(self, message: str = "Token has expired.") -> None:
        super().__init__(message)


class InvalidTokenError(AuthBaseException):
    """Raised when a JWT signature, issuer, audience, or payload structure is invalid."""
    def __init__(self, message: str = "Invalid or malformed token.") -> None:
        super().__init__(message)


class TokenRevokedError(AuthBaseException):
    """Raised when attempting to use a token marked as revoked or blacklisted."""
    def __init__(self, message: str = "Token has been revoked.") -> None:
        super().__init__(message)


class AccountLockedException(AuthBaseException):
    """Raised when account access is temporarily suspended due to repeated failed logins."""
    def __init__(self, message: str = "Account is locked due to excess login attempts.") -> None:
        super().__init__(message)


class AccountDisabledException(AuthBaseException):
    """Raised when an administrator deactivates a user account."""
    def __init__(self, message: str = "User account has been disabled.") -> None:
        super().__init__(message)


class InsufficientPermissionError(AuthBaseException):
    """Raised when an authenticated principal lacks required RBAC permissions."""
    def __init__(self, required_permission: str) -> None:
        message = f"Insufficient permissions. Required: '{required_permission}'."
        super().__init__(message, details={"required_permission": required_permission})


class PasswordComplexityException(AuthBaseException):
    """Raised when a submitted password fails strict complexity checks."""
    def __init__(self, reasons: list[str]) -> None:
        message = "Password does not meet organizational security policy."
        super().__init__(message, details={"reasons": reasons})