"""
Pydantic v2 DTO Schemas for Nutrition Telemetry and Rule Engine Recommendations.
"""

from datetime import date, datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, Field, ConfigDict, FieldValidationInfo, field_validator


class NutritionLogBase(BaseModel):
    log_date: date = Field(default_factory=date.today, description="Date of nutrition log")
    calories_kcal: Optional[float] = Field(None, ge=0, le=10000, description="Total daily calories in kcal")
    protein_grams: Optional[float] = Field(None, ge=0, le=500, description="Daily protein intake in grams")
    fluid_intake_ml: Optional[float] = Field(None, ge=0, le=10000, description="Daily fluid intake in mL")
    fruit_servings: Optional[int] = Field(None, ge=0, le=20, description="Fruit servings count")
    vegetable_servings: Optional[int] = Field(None, ge=0, le=20, description="Vegetable servings count")
    appetite_score: Optional[int] = Field(None, ge=1, le=10, description="Appetite rating from 1 (poor) to 10 (excellent)")
    food_tolerance: Optional[str] = Field(None, max_length=100, description="E.g., Good, Nausea, Vomiting, Early Satiety")
    skipped_meals: Optional[bool] = Field(False, description="Flag indicating if any main meals were skipped")
    foods_avoided: Optional[str] = Field(None, description="Free text notes on avoided foods or intolerances")
    clinician_notes: Optional[str] = Field(None, description="Notes recorded by care team")


class NutritionLogCreate(NutritionLogBase):
    patient_id: uuid.UUID = Field(..., description="Target patient profile UUID")


class NutritionLogRead(NutritionLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime


class NutritionRecommendationItem(BaseModel):
    category: str = Field(..., description="Category: Hydration, Protein, Meal Consistency, or Side Effect Management")
    severity: str = Field(..., description="Severity level: info, warning, alert")
    title: str = Field(..., description="Concise headline recommendation")
    recommendation: str = Field(..., description="Evidence-based informational guidance")
    actionable_tip: str = Field(..., description="Practical lifestyle tip for the patient")


class NutritionRecommendationResponse(BaseModel):
    patient_id: uuid.UUID
    assessment_date: date
    overall_status: str = Field(..., description="Overall nutrition status summary")
    recommendations: List[NutritionRecommendationItem] = Field(default_factory=list)
    disclaimer: str = Field(
        default="Informational guidance only. Does not constitute medical diagnosis or replace clinical care.",
        description="Standard medical disclaimer",
    )


class NutritionLogListResponse(BaseModel):
    items: List[NutritionLogRead]
    total: int
    page: int
    page_size: int