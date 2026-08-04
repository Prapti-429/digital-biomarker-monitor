"""
Database Connection & Session Lifecycle Management.

Configures the SQLAlchemy 2.0 Engine, session factory, and provides clean
FastAPI dependency injection utilities for request-scoped database sessions.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Construct thread-safe SQLAlchemy engine with dynamic connection pooling
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,  # Proactively test stale connections before issuing queries
)

# Thread-local session factory for manual transactional scopes
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a request-scoped database session.
    
    Guarantees session teardown and rollback upon unhandled exceptions.
    
    Yields:
        Session: Active SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as exc:
        logger.error("Database session exception encountered: %s", exc, exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()