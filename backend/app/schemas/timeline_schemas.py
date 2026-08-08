"""
Pydantic v2 DTO Schemas for Unified Longitudinal Clinical Master Timeline.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
from pydantic import BaseModel, Field


class TimelineEventItem(BaseModel):
    event_id: str = Field(..., description="Unique event identifier or UUID string")
    event_type: str = Field(..., description="Type: VITAL_SIGNS, LAB_RESULT, SYMPTOM, MEDICATION, NUTRITION, FILE_UPLOAD")
    timestamp: datetime = Field(..., description="Event occurrence timestamp")
    title: str = Field(..., description="Short event title or test name")
    subtitle: Optional[str] = Field(None, description="Category, dosage, or measurement summary")
    severity_indicator: str = Field(default="normal", description="Severity tag: normal, warning, alert, info")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event-specific metadata payload")


class ClinicalTimelineResponse(BaseModel):
    patient_id: uuid.UUID
    total_events: int
    page: int
    page_size: int
    events: List[TimelineEventItem] = Field(default_factory=list)