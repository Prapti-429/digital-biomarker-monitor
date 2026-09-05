"""Database engine and FastAPI session dependency."""

import logging
import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_engine(database_uri: str):
    if database_uri.startswith("sqlite"):
        return create_engine(
            database_uri,
            connect_args={"check_same_thread": False},
            echo=settings.DB_ECHO,
        )
    return create_engine(
        database_uri,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
    )


def _get_database_uri() -> str:
    value = (os.environ.get("DATABASE_URL") or settings.DATABASE_URL or "").strip()
    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://"):]
    if value:
        return value
    return settings.SQLALCHEMY_DATABASE_URI


DATABASE_URI = _get_database_uri()
engine = _build_engine(DATABASE_URI)

# In production, fail loudly if Neon is unavailable instead of silently using
# an ephemeral local SQLite database. Silent fallback breaks authentication and
# makes user accounts disappear across Render restarts/redeploys.
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    logger.info("Database connection established: %s", engine.url.get_backend_name())
except Exception:
    logger.exception("Database connection failed for %s", engine.url.get_backend_name())
    engine.dispose()
    raise

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        logger.error("Database session exception: %s", exc, exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
