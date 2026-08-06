"""
Laboratory Results and Biomarker Pydantic v2 Schemas.

Validates clinical lab results with support for CML BCR-ABL1 IS % quantitative PCR data.
"""

from datetime import date, datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, ConfigDict, Field


class LabResultBase(BaseModel):
    """Base schema for clinical laboratory data."""

    test_category: str = Field(..., max_length=100, description="Category (e.g. Molecular Diagnostics, CBC, LFT)")
    test_name: str = Field(..., max_length=150, description="Specific test name (e.g. BCR-ABL1 Major PCR)")
    numerical_value: Optional[float] = Field(None, description="Quantitative value")
    text_value: Optional[str] = Field(None, max_length=100, description="Qualitative string value if non-numeric")
    unit: Optional[str] = Field(None, max_length=50, description="Measurement units (e.g. % IS, 10^3/uL)")
    reference_range: Optional[str] = Field(None, max_length=100, description="Clinical reference range")
    is_abnormal: Optional[bool] = Field(False, description="Flag indicating value falls outside reference bounds")
    collection_date: date = Field(..., description="Specimen collection date")
    laboratory_name: Optional[str] = Field(None, max_length=150)
    verification_status: str = Field("Verified", max_length=50)
    clinician_comments: Optional[str] = Field(None)


class LabResultCreate(LabResultBase):
    """Payload to record a new laboratory result."""

    patient_id: uuid.UUID = Field(..., description="Target Patient UUID")


class LabResultUpdate(BaseModel):
    """Payload to update an existing laboratory record."""

    test_category: Optional[str] = Field(None, max_length=100)
    test_name: Optional[str] = Field(None, max_length=150)
    numerical_value: Optional[float] = None
    text_value: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    reference_range: Optional[str] = Field(None, max_length=100)
    is_abnormal: Optional[bool] = None
    collection_date: Optional[date] = None
    laboratory_name: Optional[str] = Field(None, max_length=150)
    verification_status: Optional[str] = Field(None, max_length=50)
    clinician_comments: Optional[str] = None


class LabResultRead(LabResultBase):
    """Read schema for laboratory records."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime


class LabResultListResponse(BaseModel):
    """Paginated envelope for laboratory results."""

    items: List[LabResultRead]
    total: int
    page: int
    page_size: int
    pages: int