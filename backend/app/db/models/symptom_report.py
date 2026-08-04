"""
Symptom Report ORM Model.

Stores participant self-reported physical and mental state metrics.
"""

from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.daily_check_in import DailyCheckIn


class SymptomReport(Base, UUIDMixin, TimestampMixin):
    """
    Subjective questionnaire data collected during a check-in.
    """

    __tablename__ = "symptom_reports"

    check_in_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_check_ins.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        doc="Foreign key linking to the parent daily check-in session.",
    )
    fatigue_level: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Self-reported fatigue score (e.g., scale 0-10).",
    )
    pain_level: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Self-reported pain severity score (e.g., scale 0-10).",
    )
    sleep_quality: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Perceived sleep quality score (e.g., scale 0-10).",
    )
    mood_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Self-reported mood assessment score (e.g., scale 0-10).",
    )
    appetite_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Self-reported appetite score (e.g., scale 0-10).",
    )
    energy_level: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Perceived energy level score (e.g., scale 0-10).",
    )
    nausea_level: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Self-reported nausea level score (e.g., scale 0-10).",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Qualitative symptom observations or text comments.",
    )

    # Relationships
    daily_check_in: Mapped["DailyCheckIn"] = relationship(
        "DailyCheckIn",
        back_populates="symptom_report",
        doc="Parent daily check-in session reference.",
    )

    def __repr__(self) -> str:
        return f"<SymptomReport(id={self.id}, check_in_id={self.check_in_id}, fatigue={self.fatigue_level}, pain={self.pain_level})>"