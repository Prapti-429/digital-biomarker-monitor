"""
Symptom Tracking ORM Model.

Models subjective patient symptom reports, duration, onset, and severity progression.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Integer,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from database import Base
except ImportError:
    from app.database import Base  # type: ignore

if TYPE_CHECKING:
    from app.db.models.patient import PatientProfile


class SymptomLog(Base):
    """
    Represents a logged subjective symptom event.
    """
    __tablename__ = "symptom_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    symptom_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g., "Fatigue", "Nausea", "Bone Pain", "Pleural Effusion"
    severity: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 (Mild) to 10 (Severe)
    frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "Intermittent", "Constant"
    duration: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "2 hours", "All day"
    onset: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    progression: Mapped[Optional[str]] = mapped_column(
        String(50), default="Stable", nullable=True  # "Improving", "Worsening", "Stable"
    )
    
    patient_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    patient: Mapped["PatientProfile"] = relationship("PatientProfile", back_populates="symptoms")

    __table_args__ = (
        Index("idx_symptoms_patient_time", "patient_id", "recorded_at"),
    )