"""File upload REST API and extracted-analysis responses."""
from typing import Annotated, Optional
import json
import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.session import get_db
from app.db.models import User
from app.db.models.file_upload import FileUploadRecord
from app.api.dependencies import get_current_user
from app.services.storage_service import StorageService
from app.schemas.upload_schemas import FileUploadResponse, FileUploadListResponse

router = APIRouter(prefix="/uploads", tags=["Multimodal Media & File Storage"])


def _response(record: FileUploadRecord) -> FileUploadResponse:
    analysis = None
    if record.notes:
        try:
            payload = json.loads(record.notes)
            if isinstance(payload, dict) and isinstance(payload.get("analysis"), dict):
                analysis = payload["analysis"]
        except (TypeError, ValueError):
            analysis = None
    return FileUploadResponse.model_validate({
        "id": record.id,
        "patient_id": record.patient_id,
        "file_category": record.file_category,
        "original_filename": record.original_filename,
        "file_size_bytes": record.file_size_bytes,
        "mime_type": record.mime_type,
        "processing_status": record.processing_status,
        "notes": record.notes,
        "analysis": analysis,
        "created_at": record.created_at,
    })


@router.post("", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_asset(
    patient_id: Annotated[uuid.UUID, Form(...)],
    file_category: Annotated[str, Form(...)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileUploadResponse:
    """Upload, extract available measurements/text, persist them, and return them in the same response."""
    record = await StorageService(db).save_upload(file=file, patient_id=patient_id, file_category=file_category, user_id=current_user.id)
    return _response(record)


@router.get("/patient/{patient_id}", response_model=FileUploadListResponse, status_code=status.HTTP_200_OK)
def get_patient_file_assets(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    category: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> FileUploadListResponse:
    query = select(FileUploadRecord).filter(FileUploadRecord.patient_id == patient_id)
    if category:
        query = query.filter(FileUploadRecord.file_category == category)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(db.scalars(query.order_by(FileUploadRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all())
    return FileUploadListResponse(items=[_response(i) for i in items], total=total, page=page, page_size=page_size)
