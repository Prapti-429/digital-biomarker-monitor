"""
Nutrition and Lifestyle Telemetry Pydantic v2 Schemas.

Validates daily nutrition, hydration, sleep quality, and physical activity logs.
"""

from datetime import date, datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, ConfigDict, Field


class NutritionLogBase(BaseModel):
    """Base schema for daily nutrition tracking."""

    log_date: date = Field(..., description="Log entry date")
    calories_kcal: Optional[float] = Field(None, ge=0.0, le=10000.0)
    protein_grams: Optional[float] = Field(None, ge=0.0, le=1000.0)
    fluid_intake_ml: Optional[float] = Field(None, ge=0.0, le=10000.0)
    appetite_score: Optional[int] = Field(None, ge=1, le=5, description="Appetite rating (1 = Poor, 5 = Excellent)")
    food_tolerance: Optional[str] = Field(None, max_length=100)
    foods_avoided: Optional[str] = Field(None)
    clinician_notes: Optional[str] = Field(None)


class NutritionLogCreate(NutritionLogBase):
    """Payload to log daily nutrition."""

    patient_id: uuid.UUID = Field(..., description="Target Patient UUID")


class NutritionLogRead(NutritionLogBase):
    """Read schema for nutrition logs."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime


class LifestyleLogBase(BaseModel):
    """Base schema for daily exercise, sleep, and routine telemetry."""

    log_date: date = Field(..., description="Log entry date")
    sleep_hours: Optional[float] = Field(None, ge=0.0, le=24.0)
    sleep_quality: Optional[str] = Field(None, max_length=50)
    exercise_minutes: Optional[int] = Field(None, ge=0, le=1440)
    step_count: Optional[int] = Field(None, ge=0, le=100000)
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Stress level (1 = Low, 10 = Extreme)")
    overall_energy_level: Optional[int] = Field(None, ge=1, le=5, description="Energy rating (1 = Exhausted, 5 = High)")


class LifestyleLogCreate(LifestyleLogBase):
    """Payload to log daily lifestyle telemetry."""

    patient_id: uuid.UUID = Field(..., description="Target Patient UUID")


class LifestyleLogRead(LifestyleLogBase):
    """Read schema for lifestyle logs."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime


class NutritionLogListResponse(BaseModel):
    """Paginated collection envelope for nutrition logs."""

    items: List[NutritionLogRead]
    total: int
    page: int
    page_size: int
    pages: int


class LifestyleLogListResponse(BaseModel):
    """Paginated collection envelope for lifestyle logs."""

    items: List[LifestyleLogRead]
    total: int
    page: int
    page_size: int
    pages: int