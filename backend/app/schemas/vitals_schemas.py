"""
Vital Signs Telemetry Pydantic v2 Schemas.

Validates time-series physiological measurements and subjective functional ratings.
"""

from datetime import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, ConfigDict, Field, computed_field


class VitalSignsBase(BaseModel):
    """Base schema for vital sign telemetry."""

    recorded_at: Optional[datetime] = Field(None, description="Timestamp of recording; defaults to UTC now if omitted")
    weight_kg: Optional[float] = Field(None, gt=0.0, lt=500.0, description="Body weight in kilograms")
    systolic_bp: Optional[int] = Field(None, gt=30, lt=300, description="Systolic blood pressure (mmHg)")
    diastolic_bp: Optional[int] = Field(None, gt=20, lt=200, description="Diastolic blood pressure (mmHg)")
    heart_rate_bpm: Optional[int] = Field(None, gt=20, lt=250, description="Heart rate in beats per minute")
    respiratory_rate: Optional[int] = Field(None, gt=4, lt=60, description="Breaths per minute")
    temperature_celsius: Optional[float] = Field(None, gt=30.0, lt=45.0, description="Body temperature in Celsius")
    spo2_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Blood oxygen saturation percentage")
    pain_score: Optional[int] = Field(None, ge=0, le=10, description="Pain rating scale (0 to 10)")
    fatigue_score: Optional[int] = Field(None, ge=0, le=10, description="Fatigue rating scale (0 to 10)")
    activity_level: Optional[str] = Field(None, max_length=50)
    measurement_source: str = Field("Patient Wearable/Manual", max_length=50)
    notes: Optional[str] = Field(None)


class VitalSignsCreate(VitalSignsBase):
    """Payload to log a set of vital signs."""

    patient_id: uuid.UUID = Field(..., description="Target Patient UUID")


class VitalSignsRead(VitalSignsBase):
    """Read schema for vital sign records with automated BMI computation if height is provided."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    recorded_at: datetime
    bmi: Optional[float] = None
    created_at: datetime


class VitalSignsListResponse(BaseModel):
    """Paginated collection envelope for vital signs telemetry."""

    items: List[VitalSignsRead]
    total: int
    page: int
    page_size: int
    pages: int