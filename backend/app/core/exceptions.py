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