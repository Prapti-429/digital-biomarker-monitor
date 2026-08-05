import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Enum
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ==========================================
# ENUMS
# ==========================================
class UserRole(str, enum.Enum):
    PATIENT = "patient"
    CLINICIAN = "clinician"
    ADMIN = "admin"

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# ==========================================
# MODELS
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient_profile = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    medical_history_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    check_ins = relationship("DailyCheckIn", back_populates="patient", cascade="all, delete-orphan")


class DailyCheckIn(Base):
    __tablename__ = "daily_check_ins"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    check_in_date = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="check_ins")
    audio_records = relationship("AudioRecord", back_populates="check_in", cascade="all, delete-orphan")
    video_records = relationship("VideoRecord", back_populates="check_in", cascade="all, delete-orphan")
    symptoms = relationship("Symptom", back_populates="check_in", cascade="all, delete-orphan")
    ai_results = relationship("AIResult", back_populates="check_in", cascade="all, delete-orphan")


class AudioRecord(Base):
    __tablename__ = "audio_records"

    id = Column(Integer, primary_key=True, index=True)
    check_in_id = Column(Integer, ForeignKey("daily_check_ins.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)  # S3 URL or local path
    duration_seconds = Column(Float, nullable=True)
    sampling_rate = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    check_in = relationship("DailyCheckIn", back_populates="audio_records")


class VideoRecord(Base):
    __tablename__ = "video_records"

    id = Column(Integer, primary_key=True, index=True)
    check_in_id = Column(Integer, ForeignKey("daily_check_ins.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)  # S3 URL or local path
    duration_seconds = Column(Float, nullable=True)
    fps = Column(Integer, nullable=True)
    resolution = Column(String, nullable=True)  # e.g., "1920x1080"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    check_in = relationship("DailyCheckIn", back_populates="video_records")


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    check_in_id = Column(Integer, ForeignKey("daily_check_ins.id", ondelete="CASCADE"), nullable=False)
    symptom_name = Column(String, nullable=False)  # e.g., "Tremor", "Speech slurring", "Fatigue"
    severity_score = Column(Integer, nullable=False)  # Scale 1-10 or 1-5
    additional_notes = Column(Text, nullable=True)

    # Relationships
    check_in = relationship("DailyCheckIn", back_populates="symptoms")


class AIResult(Base):
    __tablename__ = "ai_results"

    id = Column(Integer, primary_key=True, index=True)
    check_in_id = Column(Integer, ForeignKey("daily_check_ins.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(String, nullable=False)       # e.g., "VoiceBiomarkerNet-v2"
    model_version = Column(String, nullable=False)    # e.g., "1.0.4"
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    
    # Biomarker outputs & scores
    risk_score = Column(Float, nullable=True)          # e.g., 0.85
    biomarker_features = Column(JSON, nullable=True)  # Extracted features (spectrograms, facial mesh deltas)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    check_in = relationship("DailyCheckIn", back_populates="ai_results")