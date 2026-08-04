"""
Audio Recording Metadata ORM Model.

Stores metadata regarding vocal/speech acoustic assets uploaded during a check-in.
"""

from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.daily_check_in import DailyCheckIn


class AudioRecording(Base, UUIDMixin, TimestampMixin):
    """
    Acoustic recording asset metadata record.
    """

    __tablename__ = "audio_recordings"

    check_in_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_check_ins.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        doc="Foreign key linking to the parent daily check-in session.",
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Original client filename of the acoustic file.",
    )
    storage_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Relative or cloud storage URI path where the raw audio resides.",
    )
    duration_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Duration of the acoustic recording in seconds.",
    )
    sampling_rate_hz: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Audio sampling rate in Hertz (e.g., 16000, 44100).",
    )
    channels: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=1,
        nullable=True,
        doc="Number of audio channels (e.g., 1 for mono, 2 for stereo).",
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        String(64),
        default="audio/wav",
        nullable=True,
        doc="MIME format string (e.g., audio/wav, audio/m4a).",
    )

    # Relationships
    daily_check_in: Mapped["DailyCheckIn"] = relationship(
        "DailyCheckIn",
        back_populates="audio_recording",
        doc="Parent daily check-in session reference.",
    )

    def __repr__(self) -> str:
        return f"<AudioRecording(id={self.id}, check_in_id={self.check_in_id}, filename='{self.filename}')>"