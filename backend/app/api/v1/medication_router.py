"""
Medication Regimen REST Router (/api/v1/medications).

Exposes endpoints for prescribing TKI regimens, retrieving patient medications,
and logging daily dosage adherence events.
"""

from typing import Annotated, Optional, List
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

try:
    from app.database import get_db
except ImportError:
    from database import get_db  # type: ignore

from app.db.models import User
from app.api.dependencies import get_current_user, get_client_ip, RequireRole
from app.services.clinical_service import ClinicalService
from app.schemas.medication_schemas import (
    MedicationRegimenCreate,
    MedicationRegimenRead,
    MedicationAdherenceLogCreate,
    MedicationAdherenceLogRead,
)
from app.schemas.auth_enums import UserRole

router = APIRouter(prefix="/medications", tags=["Medication Management"])


@router.post(
    "/regimens",
    response_model=MedicationRegimenRead,
    status_code=status.HTTP_201_CREATED,
    summary="Prescribe a new medication regimen (Clinician / Admin only)",
    dependencies=[
        Depends(RequireRole([UserRole.ADMINISTRATOR, UserRole.ADMIN, UserRole.CLINICIAN, UserRole.DOCTOR]))
    ],
)
def create_medication_regimen(
    payload: MedicationRegimenCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    ip_address: Annotated[Optional[str], Depends(get_client_ip)] = None,
) -> MedicationRegimenRead:
    """Prescribes a new medication regimen for a patient."""
    service = ClinicalService(db)
    regimen = service.add_medication_regimen(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=ip_address,
    )
    return MedicationRegimenRead.model_validate(regimen)


@router.get(
    "/patient/{patient_id}",
    response_model=List[MedicationRegimenRead],
    status_code=status.HTTP_200_OK,
    summary="Get patient medication regimens",
)
def get_patient_medications(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    active_only: bool = Query(False, description="Filter active regimens only"),
) -> List[MedicationRegimenRead]:
    """Retrieves all medication regimens prescribed for a target patient."""
    service = ClinicalService(db)
    return service.get_patient_medications(
        patient_id=patient_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        active_only=active_only,
    )


@router.post(
    "/adherence",
    response_model=MedicationAdherenceLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log daily medication adherence event",
)
def log_medication_adherence(
    payload: MedicationAdherenceLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    ip_address: Annotated[Optional[str], Depends(get_client_ip)] = None,
) -> MedicationAdherenceLogRead:
    """Logs an individual dosage administration event (taken or missed)."""
    service = ClinicalService(db)
    log_entry = service.log_medication_adherence(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=ip_address,
    )
    return MedicationAdherenceLogRead.model_validate(log_entry)