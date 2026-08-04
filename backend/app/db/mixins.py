"""
Reusable SQLAlchemy 2.0 ORM Mixins.

Provides abstract mixin classes for primary key generation, temporal auditing,
and soft-delete capability across all research domain models.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


def utc_now() -> datetime:
    """
    Returns the current time in explicit UTC timezone.
    
    Returns:
        datetime: Timezone-aware UTC timestamp.
    """
    return datetime.now(timezone.utc)


class UUIDPrimaryKeyMixin:
    """
    Mixin providing a UUID v4 primary key column.
    
    Uses native PostgreSQL UUID type when running on Postgres, falling back to
    standard UUID representation elsewhere.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier (UUID v4)",
    )


class TimestampMixin:
    """
    Mixin providing automatic created_at and updated_at UTC timestamps.
    
    Timestamps are stored as timezone-aware UTC DateTime instances.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        comment="Timestamp when record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
        comment="Timestamp when record was last updated (UTC)",
    )


class SoftDeleteMixin:
    """
    Mixin adding soft-delete capability to domain models.
    
    Includes an indexed deleted_at timestamp column and helper properties/methods
    to check and perform soft deletion.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        index=True,
        comment="Timestamp when record was soft-deleted (UTC), null if active",
    )

    @property
    def is_deleted(self) -> bool:
        """
        Indicates whether the entity instance is soft-deleted.

        Returns:
            bool: True if deleted_at is populated, False otherwise.
        """
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """
        Marks the entity as soft-deleted by setting deleted_at to current UTC time.
        """
        self.deleted_at = utc_now()

    def restore(self) -> None:
        """
        Restores a soft-deleted entity by clearing the deleted_at timestamp.
        """
        self.deleted_at = None