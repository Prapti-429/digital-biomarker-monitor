"""Schemas for multimodal longitudinal digital-biomarker inference."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AIAnalysisRequest(BaseModel):
    """Features collected during one monitoring session.

    All sensor modalities are optional so a missing microphone/camera or an
    unusable signal does not prevent an analysis from running.
    """
    fatigue: float = Field(ge=0, le=10)
    mood_deviation: float = Field(ge=0, le=1)
    symptom_burden: float = Field(default=0, ge=0, le=1)

    # Voice / speech
    voice_rms: Optional[float] = Field(default=None, ge=0)
    voice_zero_crossing_rate: Optional[float] = Field(default=None, ge=0, le=1)
    voice_pitch_hz: Optional[float] = Field(default=None, ge=50, le=1000)
    voice_speech_activity: Optional[float] = Field(default=None, ge=0, le=1)
    voice_speech_rate: Optional[float] = Field(default=None, ge=0, le=10)
    voice_pause_ratio: Optional[float] = Field(default=None, ge=0, le=1)
    voice_language: Optional[str] = Field(default=None, max_length=20)

    # Facial / eye dynamics
    face_motion: Optional[float] = Field(default=None, ge=0)
    face_luminance_variability: Optional[float] = Field(default=None, ge=0)
    face_blink_proxy: Optional[float] = Field(default=None, ge=0, le=1)
    blink_rate_per_minute: Optional[float] = Field(default=None, ge=0, le=120)
    eye_opening_proxy: Optional[float] = Field(default=None, ge=0, le=1)

    # Movement / gait proxies from camera capture
    gait_motion: Optional[float] = Field(default=None, ge=0)
    gait_variability: Optional[float] = Field(default=None, ge=0)
    gait_symmetry_proxy: Optional[float] = Field(default=None, ge=0, le=1)

    # Breathing / respiratory motion proxies
    breathing_rate_per_minute: Optional[float] = Field(default=None, ge=0, le=60)
    breathing_variability: Optional[float] = Field(default=None, ge=0)

    # Head dynamics
    head_motion: Optional[float] = Field(default=None, ge=0)
    head_motion_variability: Optional[float] = Field(default=None, ge=0)

    source_duration_seconds: float = Field(default=0, ge=0, le=300)


class BiomarkerFeatureRead(BaseModel):
    name: str
    category: str
    value: float
    deviation: Optional[float] = None


class AIAnalysisResponse(BaseModel):
    check_in_id: UUID
    overall_score: float = Field(ge=0, le=100)
    trend: str
    confidence: float = Field(ge=0, le=1)
    model_name: str
    model_version: str
    baseline_observations: int
    explanation: str
    features: List[BiomarkerFeatureRead]
    generated_at: datetime
    data_quality_score: float = Field(ge=0, le=1, default=0)
    modalities_present: List[str] = Field(default_factory=list)
    top_drivers: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    missing_modalities: List[str] = Field(default_factory=list)
    persistence_signal: str = "INSUFFICIENT_HISTORY"
    model_config = ConfigDict(from_attributes=True)


class AIHistoryPoint(BaseModel):
    check_in_id: UUID
    score: float
    trend: str
    confidence: float
    generated_at: datetime


class AIHistoryResponse(BaseModel):
    items: List[AIHistoryPoint]
    baseline_observations: int
    model_name: str
    model_version: str
