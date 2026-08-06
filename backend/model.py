"""
Database ORM Models for the Digital Biomarker Platform.
"""

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

# Declarative Base for database mapping
Base = declarative_base()

# Import Auth Models for User Relationships
from app.db.models.auth_models import Role, UserSession


# =============================================================================
# ENUMS
# =============================================================================

class UserRole(str, enum.Enum):
    """System-wide user roles."""
    PATIENT = "patient"
    CLINICIAN = "clinician"
    RESEARCHER = "researcher"
    ADMINISTRATOR = "administrator"
    ADMIN = "admin"  # Retained for backward compatibility


class ProcessingStatus(str, enum.Enum):
    """Pipeline processing statuses for multimodal biomarker AI analyses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# CORE USER & IDENTITY MODELS
# =============================================================================

class User(Base):
    """
    Core User entity extended with Module 4 Authentication, Security,
    Account Lockout, and RBAC properties.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.PATIENT, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Security & Lockout Extensions
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    patient_profile: Mapped[Optional["Patient"]] = relationship(
        "Patient", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    assigned_roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )


class Patient(Base):
    """Clinical profile entity representing patient demographic data."""
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    medical_history_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="patient_profile")
    check_ins: Mapped[List["DailyCheckIn"]] = relationship(
        "DailyCheckIn", back_populates="patient", cascade="all, delete-orphan"
    )


# =============================================================================
# CLINICAL TELEMETRY & MULTIMODAL DOMAIN MODELS
# =============================================================================

class DailyCheckIn(Base):
    """Daily check-in logs submitted by patients."""
    __tablename__ = "daily_check_ins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    check_in_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="check_ins")
    audio_records: Mapped[List["AudioRecord"]] = relationship(
        "AudioRecord", back_populates="check_in", cascade="all, delete-orphan"
    )
    video_records: Mapped[List["VideoRecord"]] = relationship(
        "VideoRecord", back_populates="check_in", cascade="all, delete-orphan"
    )
    symptoms: Mapped[List["Symptom"]] = relationship(
        "Symptom", back_populates="check_in", cascade="all, delete-orphan"
    )
    ai_results: Mapped[List["AIResult"]] = relationship(
        "AIResult", back_populates="check_in", cascade="all, delete-orphan"
    )


class AudioRecord(Base):
    """Metadata for voice biomarker audio recordings."""
    __tablename__ = "audio_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    check_in_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("daily_check_ins.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sampling_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    check_in: Mapped["DailyCheckIn"] = relationship("DailyCheckIn", back_populates="audio_records")


class VideoRecord(Base):
    """Metadata for facial and motor video recordings."""
    __tablename__ = "video_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    check_in_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("daily_check_ins.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    check_in: Mapped["DailyCheckIn"] = relationship("DailyCheckIn", back_populates="video_records")


class Symptom(Base):
    """Patient-reported symptom instances and severity metrics."""
    __tablename__ = "symptoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    check_in_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("daily_check_ins.id", ondelete="CASCADE"), nullable=False
    )
    symptom_name: Mapped[str] = mapped_column(String(255), nullable=False)
    severity_score: Mapped[int] = mapped_column(Integer, nullable=False)
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    check_in: Mapped["DailyCheckIn"] = relationship("DailyCheckIn", back_populates="symptoms")


class AIResult(Base):
    """AI biomarker inference outputs and digital health risk scores."""
    __tablename__ = "ai_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    check_in_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("daily_check_ins.id", ondelete="CASCADE"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False
    )

    # Biomarker outputs & scores
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    biomarker_features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    summary_report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    check_in: Mapped["DailyCheckIn"] = relationship("DailyCheckIn", back_populates="ai_results")