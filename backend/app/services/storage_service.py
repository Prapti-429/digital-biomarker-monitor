"""
Storage & File Upload Handling Service.

Validates file extensions, sanitizes filenames, computes SHA-256 hashes,
and persists asset metadata to disk/DB.
"""

import hashlib
import os

from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple
import uuid

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.file_upload import FileUploadRecord


class StorageService:
    """Manages file storage, security checks, and database metadata tracking."""

    ALLOWED_EXTENSIONS = {
        "voice": {".wav", ".mp3", ".m4a", ".ogg", ".webm"},
        "video": {".mp4", ".webm", ".avi", ".mov"},
        "image": {".jpg", ".jpeg", ".png", ".webp"},
        "pdf_report": {".pdf"},
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB limit

    def __init__(self, db: Session, upload_dir: str = "uploads"):
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(
        self,
        file: UploadFile,
        patient_id: uuid.UUID,
        file_category: str,
        user_id: int,
    ) -> FileUploadRecord:
        """Sanitizes, hashes, saves file to storage directory, and records metadata."""
        if file_category not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file category '{file_category}'. Allowed: {list(self.ALLOWED_EXTENSIONS.keys())}",
            )

        file_ext = Path(file.filename or "").suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS[file_category]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{file_ext}' not permitted for category '{file_category}'.",
            )

        # Read content, calculate hash and size
        contents = await file.read()
        file_size = len(contents)

        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed limit of 50 MB.",
            )

        sha256_hash = hashlib.sha256(contents).hexdigest()

        # Generate unique stored filename
        stored_filename = f"{patient_id}_{file_category}_{uuid.uuid4().hex[:8]}{file_ext}"
        category_dir = self.upload_dir / file_category
        category_dir.mkdir(parents=True, exist_ok=True)
        file_path = category_dir / stored_filename

        # Write file to storage
        with open(file_path, "wb") as f:
            f.write(contents)

        # Create database record
        record = FileUploadRecord(
            patient_id=patient_id,
            file_category=file_category,
            original_filename=file.filename or "uploaded_file",
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_size_bytes=file_size,
            mime_type=file.content_type or "application/octet-stream",
            sha256_checksum=sha256_hash,
            processing_status="COMPLETED",
            uploaded_by_user_id=user_id,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record