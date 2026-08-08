"""
File Upload REST API Router (/api/v1/uploads).

Exposes endpoints for uploading voice, video, image, and PDF report biomarker files.
"""

from typing import Annotated, Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

try:
    from app.db.session import get_db
except ImportError:
    from app.db.session import get_db

from app.db.models import User
from app.db.models.file_upload import FileUploadRecord
from app.api.dependencies import get_current_user

try:
    from app.services.storage_service import StorageService
except ImportError:
    from services.storage_service import StorageService  # type: ignore[import-not-found]

from app.schemas.upload_schemas import FileUploadResponse, FileUploadListResponse

router = APIRouter(prefix="/uploads", tags=["Multimodal Media & File Storage"])


@router.post(
    "",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload biomarker file asset (voice, video, image, PDF)",
)
async def upload_file_asset(
    patient_id: Annotated[uuid.UUID, Form(...)],
    file_category: Annotated[str, Form(...)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileUploadResponse:
    """Accepts multipart file uploads for biomarker processing and stores file metadata."""
    storage_service = StorageService(db)
    record = await storage_service.save_upload(
        file=file,
        patient_id=patient_id,
        file_category=file_category,
        user_id=current_user.id,
    )
    return FileUploadResponse.model_validate(record)


@router.get(
    "/patient/{patient_id}",
    response_model=FileUploadListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient uploaded file assets",
)
def get_patient_file_assets(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    category: Optional[str] = Query(None, description="Filter by file_category"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> FileUploadListResponse:
    """Retrieves paginated file upload metadata for a patient."""
    query = select(FileUploadRecord).filter(FileUploadRecord.patient_id == patient_id)
    if category:
        query = query.filter(FileUploadRecord.file_category == category)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(
        db.scalars(
            query.order_by(FileUploadRecord.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )

    return FileUploadListResponse(
        items=[FileUploadResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )