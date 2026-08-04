"""
Health Stability Score ORM Model.

Stores aggregated longitudinal AI inferences for a daily session.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.daily_check_in import DailyCheckIn


class HealthStabilityScore(Base, UUIDMixin, TimestampMixin):
    """
    Consolidated health stability index and machine learning assessment result.
    """

    __tablename__ = "health_stability_scores"

    check_in_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_check_ins.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        doc="Foreign key linking to the parent daily check-in session.",
    )
    overall_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Normalized health stability index score (e.g., 0.0 to 100.0).",
    )
    trend_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Directional longitudinal trajectory (e.g., stable, improving, declining).",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Model statistical confidence metric (0.0 to 1.0).",
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp when inference analysis was generated.",
    )
    explanation_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Human-readable explanation or model interpretability rationale.",
    )
    model_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Model checkpoint version, input parameters, or SHAP attribution metrics.",
    )

    # Relationships
    daily_check_in: Mapped["DailyCheckIn"] = relationship(
        "DailyCheckIn",
        back_populates="health_stability_score",
        doc="Parent daily check-in session reference.",
    )

    def __repr__(self) -> str:
        return (
            f"<HealthStabilityScore(id={self.id}, check_in_id={self.check_in_id}, "
            f"score={self.overall_score}, trend='{self.trend_category}')>"
        )