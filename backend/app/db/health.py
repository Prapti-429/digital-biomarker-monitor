"""
Database Infrastructure Health Check Utility.

Performs proactive verification of database connectivity and measures connection
latency using lightweight SQL ping queries.
"""

import logging
import time
from typing import Any, Dict
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


def check_db_health() -> Dict[str, Any]:
    """
    Executes a simple 'SELECT 1' query against the PostgreSQL database to verify connectivity.

    Returns:
        Dict[str, Any]: Dictionary containing status ('healthy' or 'unhealthy'),
                        response time in milliseconds, and error details if applicable.
    """
    start_time = time.perf_counter()
    session = SessionLocal()
    
    try:
        # Execute basic ping query
        session.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "database": "postgresql",
            "latency_ms": latency_ms,
            "message": "Database connection established successfully.",
        }
    except SQLAlchemyError as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error("Database health check failed: %s", str(exc), exc_info=True)
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "latency_ms": latency_ms,
            "error": str(exc),
            "message": "Failed to connect to the database.",
        }
    finally:
        session.close()