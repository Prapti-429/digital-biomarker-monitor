"""
Database Initialization & Startup Utility.

Provides routines to verify database connection readiness and initialize database
metadata upon application cold start.
"""

import logging
import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


def wait_for_db(max_retries: int = 30, delay_seconds: float = 1.0) -> bool:
    """
    Waits for the PostgreSQL database to become available and accept connections.

    Args:
        max_retries (int): Maximum number of connection retry attempts.
        delay_seconds (float): Delay in seconds between connection attempts.

    Returns:
        bool: True if database connection is established, False if retries exhausted.
    """
    logger.info("Verifying PostgreSQL database availability...")
    
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("PostgreSQL database connection established successfully.")
                return True
        except OperationalError as exc:
            logger.warning(
                "Database connection attempt %d/%d failed. Retrying in %.1f seconds... (%s)",
                attempt,
                max_retries,
                delay_seconds,
                str(exc),
            )
            time.sleep(delay_seconds)

    logger.critical("Exhausted all %d attempts to connect to PostgreSQL database.", max_retries)
    return False


def init_db() -> None:
    """
    Initializes database schema metadata.
    
    Creates all tables registered with DeclarativeBase if they do not already exist.
    In production environments, Alembic migrations should be used instead.
    """
    logger.info("Initializing database schema tables from metadata...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema metadata initialized successfully.")
    except Exception as exc:
        logger.error("Failed to initialize database metadata: %s", str(exc), exc_info=True)
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if wait_for_db():
        init_db()
    else:
        raise SystemExit(1)