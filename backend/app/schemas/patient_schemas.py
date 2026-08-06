"""
Patient Profile Pydantic v2 Schemas.

Provides validation, serialization, and computed fields for patient demographics,
clinical baselines, CML disease phases, and roster responses.
"""

from datetime import date, datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, ConfigDict, Field, computed_field


class PatientBase(BaseModel):
    """Core shared demographic and clinical attributes."""

    medical_record_number: Optional[str] = Field(
        None, max_length=64, description="Optional hospital medical record number (MRN)"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Patient legal first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Patient legal last name")
    date_of_birth: date = Field(..., description="Patient date of birth")
    sex: str = Field(..., max_length=20, description="Biological sex (e.g. Male, Female, Intersex)")
    gender: Optional[str] = Field(None, max_length=50, description="Self-identified gender")
    height_cm: Optional[float] = Field(None, gt=0.0, lt=300.0, description="Patient height in centimeters")
    ethnicity: Optional[str] = Field(None, max_length=100)
    blood_group: Optional[str] = Field(None, max_length=10)
    preferred_language: str = Field("en", max_length=20)
    time_zone: str = Field("UTC", max_length=50)

    # Social History
    smoking_status: Optional[str] = Field(None, max_length=50)
    alcohol_use: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    education_level: Optional[str] = Field(None, max_length=100)

    # Emergency Contact Information
    emergency_contact_name: Optional[str] = Field(None, max_length=150)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    emergency_contact_phone: Optional[str] = Field(None, max_length=30)

    # Clinical Context (CML Focus)
    primary_diagnosis: str = Field(
        "Chronic Myeloid Leukemia (CML)", max_length=255, description="Primary oncological diagnosis"
    )
    secondary_diagnosis: Optional[str] = Field(None, max_length=255)
    disease_phase: Optional[str] = Field(
        "Chronic Phase", max_length=50, description="Disease phase (e.g. Chronic Phase, Accelerated Phase, Blast Phase)"
    )
    disease_stage: Optional[str] = Field(None, max_length=50)
    date_of_diagnosis: Optional[date] = None
    current_disease_status: Optional[str] = Field("Active Treatment", max_length=100)
    treatment_phase: Optional[str] = Field(None, max_length=100)
    hospital_affinity: Optional[str] = Field(None, max_length=255)
    treating_physician_id: Optional[int] = Field(None, description="User ID of primary treating physician")
    clinical_notes: Optional[str] = Field(None, description="Free-text clinical summary")


class PatientCreate(PatientBase):
    """Payload required to instantiate a new PatientProfile bound to a User account."""

    user_id: int = Field(..., description="Target User account ID to link with this profile")


class PatientUpdate(BaseModel):
    """Payload for partial updates of patient profiles."""

    medical_record_number: Optional[str] = Field(None, max_length=64)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    sex: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None, max_length=50)
    height_cm: Optional[float] = Field(None, gt=0.0, lt=300.0)
    ethnicity: Optional[str] = Field(None, max_length=100)
    blood_group: Optional[str] = Field(None, max_length=10)
    preferred_language: Optional[str] = Field(None, max_length=20)
    time_zone: Optional[str] = Field(None, max_length=50)

    smoking_status: Optional[str] = Field(None, max_length=50)
    alcohol_use: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    education_level: Optional[str] = Field(None, max_length=100)

    emergency_contact_name: Optional[str] = Field(None, max_length=150)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    emergency_contact_phone: Optional[str] = Field(None, max_length=30)

    primary_diagnosis: Optional[str] = Field(None, max_length=255)
    secondary_diagnosis: Optional[str] = Field(None, max_length=255)
    disease_phase: Optional[str] = Field(None, max_length=50)
    disease_stage: Optional[str] = Field(None, max_length=50)
    date_of_diagnosis: Optional[date] = None
    current_disease_status: Optional[str] = Field(None, max_length=100)
    treatment_phase: Optional[str] = Field(None, max_length=100)
    hospital_affinity: Optional[str] = Field(None, max_length=255)
    treating_physician_id: Optional[int] = None
    clinical_notes: Optional[str] = None
    is_active: Optional[bool] = None


class PatientRead(PatientBase):
    """Complete patient profile representation with computed age."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @computed_field  # type: ignore[misc]
    @property
    def age(self) -> int:
        """Calculates current age in years relative to today."""
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )


class PatientListResponse(BaseModel):
    """Paginated response envelope for patient searches and roster queries."""

    items: List[PatientRead]
    total: int
    page: int
    page_size: int
    pages: int