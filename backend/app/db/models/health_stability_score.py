"""
Health Stability Score ORM Model.

Stores aggregated AI/rule-based clinical stability metrics derived from daily telemetry.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.daily_check_in import DailyCheckIn


class HealthStabilityScore(Base, UUIDMixin, TimestampMixin):
    """
    Composite health stability score generated per monitoring session.
    """

    __tablename__ = "health_stability_scores"

    check_in_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_check_ins.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        doc="Foreign key linking to the daily check-in session.",
    )
    overall_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Composite score ranging from 0.0 (critical) to 100.0 (optimal).",
    )
    trend_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="STABLE",
        doc="Categorical indicator (e.g., IMPROVING, STABLE, DEGRADING, CRITICAL).",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        doc="Algorithm confidence score (0.0 - 1.0).",
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp when the score calculation completed.",
    )
    explanation_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Human-readable explanation of key contributing factors.",
    )
    # Dialect-agnostic JSON: Uses JSON in SQLite (pytest) & JSONB in PostgreSQL (production)
    model_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
        doc="Model versioning, factor weights, and raw feature inputs.",
    )

    # Relationships
    daily_check_in: Mapped["DailyCheckIn"] = relationship(
        "DailyCheckIn",
        back_populates="health_stability_score",
        doc="Associated daily check-in session.",
    )

    def __repr__(self) -> str:
        return (
            f"<HealthStabilityScore(id={self.id}, check_in_id={self.check_in_id}, "
            f"score={self.overall_score}, trend='{self.trend_category}')>"
        )