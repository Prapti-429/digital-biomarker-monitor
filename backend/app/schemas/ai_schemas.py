"""Schemas for the personalized multimodal digital-biomarker inference API."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AIAnalysisRequest(BaseModel):
    """Feature vector collected during one daily monitoring session."""
    fatigue: float = Field(ge=0, le=10)
    mood_deviation: float = Field(ge=0, le=1)
    symptom_burden: float = Field(default=0, ge=0, le=1)
    voice_rms: Optional[float] = Field(default=None, ge=0)
    voice_zero_crossing_rate: Optional[float] = Field(default=None, ge=0, le=1)
    voice_pitch_hz: Optional[float] = Field(default=None, ge=50, le=1000)
    voice_speech_activity: Optional[float] = Field(default=None, ge=0, le=1)
    face_motion: Optional[float] = Field(default=None, ge=0)
    face_luminance_variability: Optional[float] = Field(default=None, ge=0)
    face_blink_proxy: Optional[float] = Field(default=None, ge=0, le=1)
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
