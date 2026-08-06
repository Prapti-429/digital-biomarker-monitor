"""
Patient Profile REST Router (/api/v1/patients).

Exposes endpoints for patient profile creation, self/admin lookups, profile updates,
and clinician roster queries.
"""

from typing import Annotated, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

try:
    from app.database import get_db
except ImportError:
    from database import get_db  # type: ignore

from app.db.models import User
from app.api.dependencies import get_current_user, get_client_ip, RequireRole
from app.services.patient_service import PatientService
from app.schemas.patient_schemas import (
    PatientCreate,
    PatientUpdate,
    PatientRead,
    PatientListResponse,
)
from app.schemas.auth_enums import UserRole

router = APIRouter(prefix="/patients", tags=["Patient Management"])


@router.post(
    "",
    response_model=PatientRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a patient profile",
)
def create_patient_profile(
    payload: PatientCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    ip_address: Annotated[Optional[str], Depends(get_client_ip)] = None,
) -> PatientRead:
    """Creates a new patient profile linked to a User account."""
    service = PatientService(db)
    patient = service.create_patient_profile(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=ip_address,
    )
    return PatientRead.model_validate(patient)


@router.get(
    "/me",
    response_model=PatientRead,
    status_code=status.HTTP_200_OK,
    summary="Get current user's patient profile",
)
def get_my_patient_profile(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PatientRead:
    """Fetches the patient profile bound to the currently authenticated User."""
    service = PatientService(db)
    patient = service.get_patient_by_user_id(current_user.id)
    return PatientRead.model_validate(patient)


@router.get(
    "/{patient_id}",
    response_model=PatientRead,
    status_code=status.HTTP_200_OK,
    summary="Get patient profile by UUID",
)
def get_patient_by_id(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PatientRead:
    """Fetches a patient profile by its UUID primary key, subject to RBAC ownership checks."""
    service = PatientService(db)
    patient = service.get_patient_by_id(
        patient_id=patient_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )
    return PatientRead.model_validate(patient)


@router.patch(
    "/{patient_id}",
    response_model=PatientRead,
    status_code=status.HTTP_200_OK,
    summary="Update a patient profile",
)
def update_patient_profile(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    ip_address: Annotated[Optional[str], Depends(get_client_ip)] = None,
) -> PatientRead:
    """Updates demographic or clinical metadata for a patient profile."""
    service = PatientService(db)
    patient = service.update_patient_profile(
        patient_id=patient_id,
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=ip_address,
    )
    return PatientRead.model_validate(patient)


@router.get(
    "",
    response_model=PatientListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search patient roster (Clinician / Admin only)",
    dependencies=[
        Depends(
            RequireRole(
                [UserRole.ADMINISTRATOR, UserRole.ADMIN, UserRole.CLINICIAN, UserRole.DOCTOR, UserRole.RESEARCHER]
            )
        )
    ],
)
def search_patient_roster(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    q: Optional[str] = Query(None, description="Search term for name, MRN, or diagnosis"),
    clinician_id: Optional[int] = Query(None, description="Filter by treating clinician User ID"),
    disease_phase: Optional[str] = Query(None, description="Filter by CML disease phase"),
    is_active: bool = Query(True, description="Filter by active status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PatientListResponse:
    """Retrieves a paginated, searchable patient directory for clinical staff."""
    service = PatientService(db)
    return service.search_patient_roster(
        query=q,
        clinician_id=clinician_id,
        disease_phase=disease_phase,
        is_active=is_active,
        page=page,
        page_size=page_size,
        actor_role=current_user.role,
        actor_id=current_user.id,
    )