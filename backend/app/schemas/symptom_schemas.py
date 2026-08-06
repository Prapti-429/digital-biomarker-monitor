"""
Symptom Tracking Pydantic v2 Schemas.

Validates patient self-reported symptoms, severity progression, and duration.
"""

from datetime import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, ConfigDict, Field


class SymptomLogBase(BaseModel):
    """Base schema for subjective symptom reports."""

    symptom_name: str = Field(..., min_length=1, max_length=100, description="Symptom name (e.g. Fatigue, Pleural Effusion)")
    severity: int = Field(..., ge=1, le=10, description="Severity score from 1 (Mild) to 10 (Severe)")
    frequency: Optional[str] = Field(None, max_length=50, description="Frequency (e.g. Intermittent, Constant)")
    duration: Optional[str] = Field(None, max_length=50, description="Duration (e.g. 2 hours, All day)")
    onset: Optional[datetime] = Field(None, description="Timestamp of symptom onset")
    progression: Optional[str] = Field("Stable", max_length=50, description="Progression trend (Improving, Worsening, Stable)")
    patient_notes: Optional[str] = Field(None, description="Detailed subjective notes")


class SymptomLogCreate(SymptomLogBase):
    """Payload to log a new symptom event."""

    patient_id: uuid.UUID = Field(..., description="Target Patient UUID")


class SymptomLogRead(SymptomLogBase):
    """Read schema for symptom logs."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    recorded_at: datetime


class SymptomLogListResponse(BaseModel):
    """Paginated collection envelope for symptom logs."""

    items: List[SymptomLogRead]
    total: int
    page: int
    page_size: int
    pages: int