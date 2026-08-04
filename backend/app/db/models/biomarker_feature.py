"""
Biomarker Feature ORM Model.

Stores scalar quantitative features derived from signal processing routines.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.daily_check_in import DailyCheckIn


class BiomarkerFeature(Base, UUIDMixin, TimestampMixin):
    """
    Scalar digital biomarker metric derived from audio, video, or clinical survey data.
    """

    __tablename__ = "biomarker_features"

    check_in_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_check_ins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key linking to the parent daily check-in session.",
    )
    feature_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="Unique feature identifier name (e.g., jitter_local, eye_blink_rate).",
    )
    feature_category: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="Category classification (e.g., acoustic, facial_movement, survey).",
    )
    feature_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Extracted scalar numerical value.",
    )
    source_modality: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Modality source (e.g., audio, video, multimodal).",
    )
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp when feature extraction execution completed.",
    )
    extra_properties: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Optional metadata such as feature extractor version or confidence scores.",
    )

    # Relationships
    daily_check_in: Mapped["DailyCheckIn"] = relationship(
        "DailyCheckIn",
        back_populates="biomarker_features",
        doc="Parent daily check-in session reference.",
    )

    __table_args__ = (
        Index("idx_biomarker_feature_lookup", "check_in_id", "feature_category", "feature_name"),
    )

    def __repr__(self) -> str:
        return (
            f"<BiomarkerFeature(id={self.id}, check_in_id={self.check_in_id}, "
            f"name='{self.feature_name}', value={self.feature_value})>"
        )