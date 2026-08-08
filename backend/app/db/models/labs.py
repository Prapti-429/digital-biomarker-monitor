"""
Laboratory Results and Molecular Biomarker ORM Models.

Generic lab result tracking with specialized support for CML BCR-ABL1 IS % PCR values.
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
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from app.db.base import Base
except ImportError:
    from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.patient import PatientProfile


class LabResult(Base):
    """
    Represents individual clinical laboratory test outcomes.
    """
    __tablename__ = "lab_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    test_category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g., "Molecular Diagnostics", "CBC", "LFT", "KFT"
    test_name: Mapped[str] = mapped_column(
        String(150), nullable=False, index=True
    )  # e.g., "BCR-ABL1 Major (p210) Quantitative PCR", "WBC Count"
    
    numerical_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    text_value: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "% IS", "10^3/uL"
    reference_range: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "< 0.1% IS"
    
    is_abnormal: Mapped[Optional[bool]] = mapped_column(default=False, nullable=True)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    laboratory_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="Verified", nullable=False)
    clinician_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    patient: Mapped["PatientProfile"] = relationship("PatientProfile", back_populates="labs")

    __table_args__ = (
        Index("idx_labs_patient_date", "patient_id", "collection_date"),
    )