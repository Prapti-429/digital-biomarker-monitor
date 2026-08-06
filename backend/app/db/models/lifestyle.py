"""
Nutrition and Lifestyle Telemetry ORM Models.

Logs patient daily diet, hydration, exercise, sleep, and lifestyle factors.
"""

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    Float,
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


class NutritionLog(Base):
    """
    Longitudinal daily nutrition and meal tolerance tracking.
    """
    __tablename__ = "nutrition_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    calories_kcal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    protein_grams: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fluid_intake_ml: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    appetite_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1 (Poor) to 5 (Excellent)
    food_tolerance: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "Nauseous after oral TKI"
    foods_avoided: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinician_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    patient: Mapped["PatientProfile"] = relationship("PatientProfile", back_populates="nutrition_logs")


class LifestyleLog(Base):
    """
    Longitudinal daily exercise, sleep, and routine telemetry.
    """
    __tablename__ = "lifestyle_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleep_quality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "Restful", "Fragmented"
    exercise_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    step_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1 (Low) to 10 (Extreme)
    overall_energy_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1 to 5

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    patient: Mapped["PatientProfile"] = relationship("PatientProfile", back_populates="lifestyle_logs")