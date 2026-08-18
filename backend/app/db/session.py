"""Database engine and FastAPI session dependency."""

import logging
import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
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
    return value or "sqlite:///./digital_biomarker.db"


DATABASE_URI = _get_database_uri()
engine = _build_engine(DATABASE_URI)

# Never let a bad/missing Render database connection prevent the HTTP server
# from starting. This is a prototype-safe fallback; when DATABASE_URL works,
# PostgreSQL remains the primary database.
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    logger.info("Database connection established: %s", engine.url.get_backend_name())
except SQLAlchemyError:
    if not DATABASE_URI.startswith("sqlite"):
        logger.exception("Configured database is unavailable; using local SQLite fallback")
        fallback_path = Path(__file__).resolve().parents[2] / "digital_biomarker.db"
        DATABASE_URI = f"sqlite:///{fallback_path.as_posix()}"
        engine.dispose()
        engine = _build_engine(DATABASE_URI)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.warning("Using SQLite fallback database: %s", fallback_path)
    else:
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
    except SQLAlchemyError as exc:
        logger.error("Database session exception: %s", exc, exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
