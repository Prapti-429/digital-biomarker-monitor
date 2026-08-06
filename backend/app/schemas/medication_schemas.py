"""
Medication Regimen and Adherence Pydantic v2 Schemas.

Defines schemas for managing Tyrosine Kinase Inhibitor (TKI) regimens
and longitudinal daily adherence logs.
"""

from datetime import date, datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, ConfigDict, Field


class MedicationRegimenBase(BaseModel):
    """Base schema for medication specifications."""

    medication_name: str = Field(..., min_length=1, max_length=150, description="Generic or trade medication name")
    drug_class: str = Field("Tyrosine Kinase Inhibitor", max_length=100)
    dose: str = Field(..., min_length=1, max_length=50, description="Clinical dosage string (e.g. 400mg)")
    dose_value_mg: float = Field(..., gt=0.0, description="Numerical dosage value in milligrams for analytic aggregation")
    frequency: str = Field(..., max_length=50, description="Administration frequency (e.g. Once Daily)")
    route: str = Field("Oral", max_length=50)
    start_date: date = Field(..., description="Regimen initiation date")
    end_date: Optional[date] = Field(None, description="Optional regimen completion date")
    instructions: Optional[str] = Field(None, description="Administration instructions")
    side_effects_noted: Optional[str] = Field(None, description="Documented or expected side effects")


class MedicationRegimenCreate(MedicationRegimenBase):
    """Payload to create a new medication regimen for a patient."""

    patient_id: uuid.UUID = Field(..., description="Target Patient UUID")
    prescribing_clinician_id: Optional[int] = Field(None, description="User ID of prescribing clinician")


class MedicationRegimenUpdate(BaseModel):
    """Payload to update an existing medication regimen."""

    medication_name: Optional[str] = Field(None, max_length=150)
    drug_class: Optional[str] = Field(None, max_length=100)
    dose: Optional[str] = Field(None, max_length=50)
    dose_value_mg: Optional[float] = Field(None, gt=0.0)
    frequency: Optional[str] = Field(None, max_length=50)
    route: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    instructions: Optional[str] = None
    side_effects_noted: Optional[str] = None


class MedicationRegimenRead(MedicationRegimenBase):
    """Read schema for medication regimens."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    is_active: bool
    missed_dose_counter: int
    adherence_percentage: float
    prescribing_clinician_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class MedicationAdherenceLogCreate(BaseModel):
    """Payload to log an individual dose administration event."""

    regimen_id: uuid.UUID = Field(..., description="Target Medication Regimen UUID")
    scheduled_time: datetime = Field(..., description="Scheduled administration timestamp")
    taken_time: Optional[datetime] = Field(None, description="Actual administration timestamp if taken")
    was_taken: bool = Field(..., description="Flag indicating if the dose was successfully administered")
    reason_missed: Optional[str] = Field(None, max_length=255, description="Clinical or personal reason for missed dose")
    side_effects_experienced: Optional[str] = Field(None, description="Specific side effects triggered by this dose")


class MedicationAdherenceLogRead(MedicationAdherenceLogCreate):
    """Read schema for logged adherence events."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class MedicationRegimenListResponse(BaseModel):
    """Paginated collection envelope for medication regimens."""

    items: List[MedicationRegimenRead]
    total: int
    page: int
    page_size: int
    pages: int