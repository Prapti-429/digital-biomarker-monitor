"""
Medication Regimen and Adherence ORM Models.
"""

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional, List
import uuid

from sqlalchemy import String, Text, Date, DateTime, Float, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.patient import PatientProfile
    from app.db.models.user import User


class MedicationRegimen(Base):
    __tablename__ = "medication_regimens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    medication_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    drug_class: Mapped[str] = mapped_column(String(100), default="Tyrosine Kinase Inhibitor", nullable=False)
    dose: Mapped[str] = mapped_column(String(50), nullable=False)
    dose_value_mg: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[str] = mapped_column(String(50), nullable=False)
    route: Mapped[str] = mapped_column(String(50), default="Oral", nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    missed_dose_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    adherence_percentage: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    # User.id is UUID. This foreign key must use the same UUID type.
    prescribing_clinician_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    side_effects_noted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc), nullable=True
    )

    patient: Mapped["PatientProfile"] = relationship("PatientProfile", back_populates="medications")
    adherence_logs: Mapped[List["MedicationAdherenceLog"]] = relationship(
        "MedicationAdherenceLog", back_populates="regimen", cascade="all, delete-orphan"
    )


class MedicationAdherenceLog(Base):
    __tablename__ = "medication_adherence_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    regimen_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medication_regimens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    taken_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    was_taken: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason_missed: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    side_effects_experienced: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    regimen: Mapped["MedicationRegimen"] = relationship("MedicationRegimen", back_populates="adherence_logs")
