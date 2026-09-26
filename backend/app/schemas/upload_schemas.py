"""Pydantic response schemas for uploaded assets."""
from datetime import datetime
from typing import Any, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict


class FileUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    patient_id: uuid.UUID
    file_category: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    processing_status: str
    notes: Optional[str] = None
    analysis: Optional[dict[str, Any]] = None
    created_at: datetime


class FileUploadListResponse(BaseModel):
    items: List[FileUploadResponse]
    total: int
    page: int
    page_size: int
