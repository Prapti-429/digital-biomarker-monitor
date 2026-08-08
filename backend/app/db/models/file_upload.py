"""
File Upload Record ORM Model.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from app.db.base import Base
except ImportError:
    from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.patient import PatientProfile


class FileUploadRecord(Base):
    __tablename__ = "file_upload_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    file_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # E.g., voice, video, image, pdf_report
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sha256_checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    processing_status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    uploaded_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    patient: Mapped["PatientProfile"] = relationship("PatientProfile")

    __table_args__ = (
        Index("idx_file_patient_category", "patient_id", "file_category"),
    )