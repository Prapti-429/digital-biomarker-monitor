"""
Daily Check-In ORM Model.

Serves as the temporal hub for daily multimodal digital biomarker collection.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlalchemy import Date, DateTime, ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.audio_recording import AudioRecording
    from app.db.models.biomarker_feature import BiomarkerFeature
    from app.db.models.health_stability_score import HealthStabilityScore
    from app.db.models.symptom_report import SymptomReport
    from app.db.models.user import User
    from app.db.models.video_recording import VideoRecording


class DailyCheckIn(Base, UUIDMixin, TimestampMixin):
    """
    Daily monitoring session aggregate node.
    """

    __tablename__ = "daily_check_ins"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key linking to the user submitting the check-in.",
    )
    check_in_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Target date for the daily check-in session.",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
        doc="Status of session completion (e.g., pending, completed, partial).",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Exact timestamp when the daily check-in was finalized.",
    )
    extra_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
        doc="Extensible JSON payload for device parameters or environment conditions.",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="daily_check_ins",
        doc="Parent user who created this check-in.",
    )
    audio_recording: Mapped[Optional["AudioRecording"]] = relationship(
        "AudioRecording",
        back_populates="daily_check_in",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Associated acoustic recording metadata.",
    )
    video_recording: Mapped[Optional["VideoRecording"]] = relationship(
        "VideoRecording",
        back_populates="daily_check_in",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Associated video recording metadata.",
    )
    symptom_report: Mapped[Optional["SymptomReport"]] = relationship(
        "SymptomReport",
        back_populates="daily_check_in",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Associated subjective symptom self-report.",
    )
    biomarker_features: Mapped[List["BiomarkerFeature"]] = relationship(
        "BiomarkerFeature",
        back_populates="daily_check_in",
        cascade="all, delete-orphan",
        doc="Collection of scalar features extracted from this session.",
    )
    health_stability_score: Mapped[Optional["HealthStabilityScore"]] = relationship(
        "HealthStabilityScore",
        back_populates="daily_check_in",
        uselist=False,
        cascade="all, delete-orphan",
        doc="AI generated stability assessment score for this session.",
    )

    def __repr__(self) -> str:
        return f"<DailyCheckIn(id={self.id}, user_id={self.user_id}, date={self.check_in_date}, status='{self.status}')>"