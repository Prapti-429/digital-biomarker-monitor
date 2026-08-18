"""Patient profile and demographic ORM model."""

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional, List
import uuid

from sqlalchemy import String, Text, Date, DateTime, Float, Integer, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.medication import MedicationRegimen
    from app.db.models.vitals import VitalSigns
    from app.db.models.labs import LabResult
    from app.db.models.symptoms import SymptomLog
    from app.db.models.lifestyle import NutritionLog, LifestyleLog
    from app.db.models.user import User


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    medical_record_number: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True, index=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[str] = mapped_column(String(20), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ethnicity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    time_zone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)

    smoking_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    alcohol_use: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    education_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    primary_diagnosis: Mapped[str] = mapped_column(String(255), default="Chronic Myeloid Leukemia (CML)", nullable=False)
    secondary_diagnosis: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    disease_phase: Mapped[Optional[str]] = mapped_column(String(50), default="Chronic Phase", nullable=True)
    disease_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_of_diagnosis: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    current_disease_status: Mapped[Optional[str]] = mapped_column(String(100), default="Active Treatment", nullable=True)
    treatment_phase: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    hospital_affinity: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    treating_physician_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    clinical_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="patient_profile", foreign_keys=[user_id])
    medications: Mapped[List["MedicationRegimen"]] = relationship("MedicationRegimen", back_populates="patient", cascade="all, delete-orphan")
    vitals: Mapped[List["VitalSigns"]] = relationship("VitalSigns", back_populates="patient", cascade="all, delete-orphan")
    labs: Mapped[List["LabResult"]] = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")
    symptoms: Mapped[List["SymptomLog"]] = relationship("SymptomLog", back_populates="patient", cascade="all, delete-orphan")
    nutrition_logs: Mapped[List["NutritionLog"]] = relationship("NutritionLog", back_populates="patient", cascade="all, delete-orphan")
    lifestyle_logs: Mapped[List["LifestyleLog"]] = relationship("LifestyleLog", back_populates="patient", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_patient_last_first", "last_name", "first_name"),
        Index("idx_patient_dob", "date_of_birth"),
    )
