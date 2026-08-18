from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class PatientProfile(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "patient_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    medical_record_number: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=False)
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
    primary_diagnosis: Mapped[str] = mapped_column(String(255), nullable=False)
    secondary_diagnosis: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    disease_phase: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    disease_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_of_diagnosis: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    current_disease_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    treatment_phase: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hospital_affinity: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    treating_physician_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    clinical_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped[User] = relationship(
        "User",
        back_populates="patient_profile",
        foreign_keys=[user_id],
    )
    treating_physician: Mapped[Optional[User]] = relationship(
        "User",
        foreign_keys=[treating_physician_id],
    )