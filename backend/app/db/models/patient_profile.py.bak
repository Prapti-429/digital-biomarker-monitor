"""
Patient Profile ORM Model.

Stores long-term research participant demographic and baseline clinical status.
"""

from datetime import date
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class PatientProfile(Base, UUIDMixin, TimestampMixin):
    """
    Participant demographic and clinical metadata record.
    """

    __tablename__ = "patient_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        doc="Foreign key linking to the parent user account.",
    )
    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Participant age in years at enrollment.",
    )
    sex: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        doc="Biological sex or self-reported gender identifier.",
    )
    height_cm: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Baseline height in centimeters.",
    )
    weight_kg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Baseline weight in kilograms.",
    )
    diagnosis_status: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Clinical diagnosis or cohort assignment.",
    )
    enrollment_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Date participant enrolled in the monitoring program.",
    )
    research_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Extensible research or investigator observations.",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="patient_profile",
        doc="Parent user account reference.",
    )

    def __repr__(self) -> str:
        return f"<PatientProfile(id={self.id}, user_id={self.user_id}, diagnosis_status='{self.diagnosis_status}')>"