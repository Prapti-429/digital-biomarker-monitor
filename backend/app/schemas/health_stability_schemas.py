"""
Pydantic v2 DTO Schemas for Health Stability Score (HSS) Analytics.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
from pydantic import BaseModel, Field, ConfigDict


class HealthStabilityDimensionScore(BaseModel):
    dimension: str = Field(..., description="Dimension name: Medication Adherence, Vital Signs, Symptoms, Nutrition")
    score: float = Field(..., ge=0.0, le=100.0, description="Dimension sub-score (0-100)")
    weight: float = Field(..., ge=0.0, le=1.0, description="Relative weight in overall calculation")
    weighted_contribution: float = Field(..., description="Contributed points to overall HSS")
    status: str = Field(..., description="Status tier: Optimal, Moderate, Poor, Critical")
    key_factor: str = Field(..., description="Summary statement of key contributing factors")


class HealthStabilityScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: uuid.UUID
    assessment_timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall Health Stability Score (0-100)")
    stability_tier: str = Field(..., description="Stability classification: High Stability, Moderate Risk, High Risk")
    trend_direction: str = Field(..., description="Trajectory: Improving, Stable, Deteriorating")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Confidence percentage based on data density")
    primary_risk_driver: Optional[str] = Field(None, description="Primary domain driving score down")
    
    dimensions: List[HealthStabilityDimensionScore] = Field(default_factory=list)
    explanation: str = Field(..., description="Clinical narrative summary explaining the composite score")


class HealthStabilityHistoricalPoint(BaseModel):
    timestamp: datetime
    overall_score: float
    stability_tier: str


class HealthStabilityTrendResponse(BaseModel):
    patient_id: uuid.UUID
    current_score: HealthStabilityScoreRead
    history: List[HealthStabilityHistoricalPoint] = Field(default_factory=list)
    data_points_analyzed: int