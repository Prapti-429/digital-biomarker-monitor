"""
Alembic Base Discovery Entrypoint.

Imports Declarative Base and all domain ORM models so Alembic autogenerate
can inspect Base.metadata and detect database schema migrations.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """

    id: Any
    __name__: str


class UUIDMixin:
    """
    Mixin for adding UUID primary key to ORM models.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique primary key identifier (UUIDv4).",
    )


class TimestampMixin:
    """
    Mixin for adding created_at and updated_at timestamps to ORM models.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when the record was last updated.",
    )


# Import all ORM models here so Alembic detects them under Base.metadata
from app.db.models import (  # noqa: F401, E402
    AudioRecording,
    BiomarkerFeature,
    DailyCheckIn,
    HealthStabilityScore,
    PatientProfile,
    SymptomReport,
    User,
    VideoRecording,
)