"""
Clinical Master Timeline REST API Router (/api/v1/clinical/timeline).

Exposes consolidated chronological feeds across vitals, labs, symptoms,
medications, nutrition, and biomarker file uploads.
"""

from typing import Annotated, Optional, List
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

try:
    from app.database import get_db  # type: ignore[import-not-found]
except ImportError:
    from database import get_db  # type: ignore[import-not-found]

from app.db.models import User
from app.api.dependencies import get_current_user

try:
    from app.services.timeline_service import ClinicalTimelineService
except ImportError:
    from services.timeline_service import ClinicalTimelineService  # type: ignore[import-not-found]

from app.schemas.timeline_schemas import ClinicalTimelineResponse

router = APIRouter(prefix="/clinical/timeline", tags=["Clinical Master Timeline"])


@router.get(
    "/patient/{patient_id}",
    response_model=ClinicalTimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unified chronological clinical master timeline",
)
def get_patient_clinical_timeline(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    event_types: Optional[List[str]] = Query(None, description="Filter by event types: VITAL_SIGNS, LAB_RESULT, SYMPTOM, MEDICATION, NUTRITION, FILE_UPLOAD"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=100),
) -> ClinicalTimelineResponse:
    """Retrieves unified paginated master timeline merging all telemetry dimensions chronologically."""
    service = ClinicalTimelineService(db)
    return service.get_patient_timeline(
        patient_id=patient_id,
        event_types=event_types,
        page=page,
        page_size=page_size,
    )