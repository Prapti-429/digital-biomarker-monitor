"""
Video Recording Metadata ORM Model.

Stores metadata regarding visual asset files uploaded during a daily check-in.
"""

from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.daily_check_in import DailyCheckIn


class VideoRecording(Base, UUIDMixin, TimestampMixin):
    """
    Video recording asset metadata record.
    """

    __tablename__ = "video_recordings"

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
        doc="Original client filename of the video asset.",
    )
    storage_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Storage system file path or cloud URI for the video payload.",
    )
    duration_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Total video duration in seconds.",
    )
    frame_rate_fps: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Video capture framerate in frames per second.",
    )
    resolution_width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Horizontal resolution in pixels.",
    )
    resolution_height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Vertical resolution in pixels.",
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        String(64),
        default="video/mp4",
        nullable=True,
        doc="MIME type string (e.g., video/mp4, video/webm).",
    )

    # Relationships
    daily_check_in: Mapped["DailyCheckIn"] = relationship(
        "DailyCheckIn",
        back_populates="video_recording",
        doc="Parent daily check-in session reference.",
    )

    def __repr__(self) -> str:
        return f"<VideoRecording(id={self.id}, check_in_id={self.check_in_id}, filename='{self.filename}')>"