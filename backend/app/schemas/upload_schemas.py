"""
Pydantic v2 DTO Schemas for File Uploads and Biomarker Media Assets.
"""

from datetime import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, Field, ConfigDict


class FileUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    file_category: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    processing_status: str
    created_at: datetime


class FileUploadListResponse(BaseModel):
    items: List[FileUploadResponse]
    total: int
    page: int
    page_size: int