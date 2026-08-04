"""
Database Package Core Exports.

Provides a clean unified import interface for ORM DeclarativeBase, session factories,
engine instances, dependencies, and database mixins.
"""

from app.db.base import Base
from app.db.health import check_db_health
from app.db.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.session import SessionLocal, engine, get_db

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "check_db_health",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
]