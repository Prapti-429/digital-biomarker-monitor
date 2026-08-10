"""
User ORM Model.

Represents research participant and investigator accounts within the system.
"""

from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.daily_check_in import DailyCheckIn
    from app.db.models.patient_profile import PatientProfile


class User(Base, UUIDMixin, TimestampMixin):
    """
    User account entity for authentication and participant tracking.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique email address for user authentication.",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hashed password string.",
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Full legal or research alias name of the participant.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Flag indicating if the user account is active.",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Flag indicating administrative access privileges.",
    )

    # Relationships
    patient_profile: Mapped[Optional["PatientProfile"]] = relationship(
    "PatientProfile",
    back_populates="user",
    foreign_keys="PatientProfile.user_id",
    uselist=False,
    cascade="all, delete-orphan",
)
    daily_check_ins: Mapped[List["DailyCheckIn"]] = relationship(
        "DailyCheckIn",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="DailyCheckIn.check_in_date.desc()",
        doc="Longitudinal collection of daily check-ins submitted by the user.",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', is_active={self.is_active})>"