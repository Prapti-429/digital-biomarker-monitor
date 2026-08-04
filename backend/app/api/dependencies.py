"""
API Route Dependencies.

Provides reusable FastAPI dependency functions for request-scoped database sessions,
security context, and operational health checks.
"""

import logging
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseConnectionError
from app.db.health import check_db_health
from app.db.session import get_db

logger = logging.getLogger(__name__)


def get_database_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that wraps the session generator with exception translation.

    Converts raw SQLAlchemy connection failures into clean HTTP exception responses
    if the database is unreachable during request processing.

    Yields:
        Session: Request-scoped SQLAlchemy session instance.
    """
    try:
        yield from get_db()
    except SQLAlchemyError as exc:
        logger.error("Uncaught database exception in API route context: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable.",
        ) from exc


def verify_db_connection() -> Session:
    """
    Dependency that performs an active health check before resolving a route.

    Useful for critical endpoints that require confirmed database read/write access.

    Returns:
        Session: Active database session if health check passes.
    """
    health = check_db_health()
    if health.get("status") != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection verification failed: {health.get('message')}",
        )