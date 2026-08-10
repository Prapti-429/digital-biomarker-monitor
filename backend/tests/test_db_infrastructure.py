"""
Database Infrastructure Test Suite.

Verifies database engine connection, session lifecycle, health check reporting,
and mixin behaviors for Module 3A.
"""

from datetime import datetime
import uuid
import pytest
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, Session

from app.db.base import Base
from app.db.health import check_db_health
from app.db.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.session import SessionLocal, engine, get_db


def is_postgres_reachable() -> bool:
    """Checks if a live PostgreSQL server is actively accepting connections."""
    try:
        with engine.connect() as conn:
            return True
    except Exception:
        return False


postgres_required = pytest.mark.skipif(
    not is_postgres_reachable(),
    reason="Live PostgreSQL database server not reachable locally (running in SQLite test mode)"
)


# Concrete dummy ORM model specifically designed for testing mixins in isolation
class DummyTestModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Test entity used exclusively to verify mixins and session operations.
    """

    __tablename__ = "dummy_test_records"

    name: Mapped[str] = mapped_column(String(50), nullable=False)


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """
    Creates temporary dummy table for infrastructure testing and tears it down afterwards.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@postgres_required
def test_database_engine_connection():
    """
    Verifies that the SQLAlchemy engine can establish a raw connection.
    """
    with engine.connect() as connection:
        assert connection is not None


@postgres_required
def test_session_local_lifecycle():
    """
    Tests manual SessionLocal instantiation, commit, query, and closure.
    """
    session: Session = SessionLocal()
    try:
        record = DummyTestModel(name="Infrastructure Test Record")
        session.add(record)
        session.commit()
        session.refresh(record)

        assert record.id is not None
        assert isinstance(record.id, uuid.UUID)
        assert record.name == "Infrastructure Test Record"
        assert isinstance(record.created_at, datetime)
        assert record.deleted_at is None
        assert not record.is_deleted
    finally:
        session.close()


@postgres_required
def test_fastapi_get_db_generator():
    """
    Tests the get_db dependency generator used by FastAPI endpoints.
    """
    db_gen = get_db()
    db_session = next(db_gen)

    assert isinstance(db_session, Session)

    # Run simple query to verify session validity
    stmt = select(DummyTestModel).limit(1)
    result = db_session.scalars(stmt).first()
    assert result is not None

    # Trigger teardown/cleanup phase of generator
    try:
        next(db_gen)
    except StopIteration:
        pass


@postgres_required
def test_soft_delete_mixin_behavior():
    """
    Verifies soft_delete and restore methods on ORM models.
    """
    session: Session = SessionLocal()
    try:
        record = DummyTestModel(name="Soft Delete Test")
        session.add(record)
        session.commit()

        # Perform soft delete
        record.soft_delete()
        session.commit()
        assert record.is_deleted
        assert record.deleted_at is not None

        # Restore soft delete
        record.restore()
        session.commit()
        assert not record.is_deleted
        assert record.deleted_at is None
    finally:
        session.close()


@postgres_required
def test_check_db_health_utility():
    """
    Tests the database health check utility response format.
    """
    health_status = check_db_health()
    assert health_status["status"] in ["healthy", "unhealthy"]
    assert health_status["database"] == "postgresql"
    assert "latency_ms" in health_status