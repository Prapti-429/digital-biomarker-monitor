"""
Application & Database Constants.

Defines global constant values for database statuses, error codes, and configuration defaults.
"""

from enum import Enum

# Middleware & API Header Constants
PROCESS_TIME_HEADER = "X-Process-Time"
CORRELATION_ID_HEADER = "X-Correlation-ID"


class DatabaseStatus(str, Enum):
    """
    Status enumerations for database connectivity health checks.
    """

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class DBErrorMessages:
    """
    Standardized error messages for database operational failures.
    """

    CONNECTION_FAILED = "Failed to establish a connection to the PostgreSQL database."
    TRANSACTION_FAILED = "Database transaction failed and was rolled back."
    RECORD_NOT_FOUND = "Requested database record was not found."
    HEALTH_CHECK_FAILED = "Database health check failed during connectivity probe."


# Infrastructure default timeout values (in seconds)
DEFAULT_DB_CONNECT_TIMEOUT = 10.0
DEFAULT_HEALTH_CHECK_TIMEOUT = 5.0