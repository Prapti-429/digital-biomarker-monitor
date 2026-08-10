"""
Clinical Telemetry REST Router (/api/v1/clinical).

Exposes endpoints for time-series vital signs, laboratory results (including PCR values),
symptom logs, nutrition entries, and lifestyle telemetry.
"""

from typing import Annotated, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

try:
    from app.db.session import get_db
except ImportError:
    from app.db.session import get_db

from app.db.models import User
from app.api.dependencies import get_current_user, get_client_ip, RequireRole
from app.services.clinical_service import ClinicalService
from app.schemas.vitals_schemas import VitalSignsCreate, VitalSignsRead, VitalSignsListResponse
from app.schemas.labs_schemas import LabResultCreate, LabResultRead, LabResultListResponse
from app.schemas.symptom_schemas import SymptomLogCreate, SymptomLogRead, SymptomLogListResponse
from app.schemas.lifestyle_schemas import (
    NutritionLogCreate,
    NutritionLogRead,
    NutritionLogListResponse,
    LifestyleLogCreate,
    LifestyleLogRead,
    LifestyleLogListResponse,
)
from app.schemas.auth_enums import UserRole

router = APIRouter(prefix="/clinical", tags=["Clinical Telemetry"])


# -----------------------------------------------------------------------------
# Vital Signs Telemetry Endpoints
# -----------------------------------------------------------------------------
@router.post(
    "/vitals",
    response_model=VitalSignsRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record vital signs telemetry",
)
def record_vital_signs(
    payload: VitalSignsCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    ip_address: Annotated[Optional[str], Depends(get_client_ip)] = None,
) -> VitalSignsRead:
    """Records physiological measurements and subjective functional scores."""
    service = ClinicalService(db)
    return service.record_vital_signs(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=ip_address,
    )


@router.get(
    "/vitals/patient/{patient_id}",
    response_model=VitalSignsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient vital signs history",
)
def get_patient_vitals_history(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> VitalSignsListResponse:
    """Retrieves paginated historical vital signs entries for a target patient."""
    service = ClinicalService(db)
    return service.get_vitals_telemetry(
        patient_id=patient_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        page=page,
        page_size=page_size,
    )


# -----------------------------------------------------------------------------
# Laboratory & Biomarker Endpoints
# -----------------------------------------------------------------------------
@router.post(
    "/labs",
    response_model=LabResultRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record laboratory or biomarker result (Clinician / Admin only)",
    dependencies=[
        Depends(
            RequireRole(
               [
    UserRole.ADMINISTRATOR,
    UserRole.CLINICIAN,
    UserRole.RESEARCHER,
]
            )
        )
    ],
)
def record_lab_result(
    payload: LabResultCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    ip_address: Annotated[Optional[str], Depends(get_client_ip)] = None,
) -> LabResultRead:
    """Records a new clinical laboratory outcome or BCR-ABL1 quantitative PCR biomarker."""
    service = ClinicalService(db)
    return service.record_lab_result(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=ip_address,
    )


@router.get(
    "/labs/patient/{patient_id}",
    response_model=LabResultListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient laboratory history",
)
def get_patient_labs_history(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    category: Optional[str] = Query(None, description="Filter by test category (e.g., Molecular Diagnostics, CBC)"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> LabResultListResponse:
    """Retrieves paginated laboratory results for a target patient."""
    service = ClinicalService(db)
    return service.get_patient_labs(
        patient_id=patient_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        category=category,
        page=page,
        page_size=page_size,
    )


# -----------------------------------------------------------------------------
# Symptom Tracking Endpoints
# -----------------------------------------------------------------------------
@router.post(
    "/symptoms",
    response_model=SymptomLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a patient symptom event",
)
def log_patient_symptom(
    payload: SymptomLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    ip_address: Annotated[Optional[str], Depends(get_client_ip)] = None,
) -> SymptomLogRead:
    """Logs a patient self-reported symptom event."""
    service = ClinicalService(db)
    return service.log_patient_symptom(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=ip_address,
    )


@router.get(
    "/symptoms/patient/{patient_id}",
    response_model=SymptomLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient symptom history",
)
def get_patient_symptoms_history(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> SymptomLogListResponse:
    """Retrieves paginated historical symptom reports for a patient."""
    service = ClinicalService(db)
    return service.get_patient_symptoms(
        patient_id=patient_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        page=page,
        page_size=page_size,
    )


# -----------------------------------------------------------------------------
# Nutrition & Lifestyle Endpoints
# -----------------------------------------------------------------------------
@router.post(
    "/nutrition",
    response_model=NutritionLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log daily nutrition telemetry",
)
def log_daily_nutrition(
    payload: NutritionLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NutritionLogRead:
    """Logs daily patient nutrition intake and meal tolerance."""
    service = ClinicalService(db)
    return service.log_daily_nutrition(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )


@router.get(
    "/nutrition/patient/{patient_id}",
    response_model=NutritionLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient nutrition history",
)
def get_patient_nutrition_history(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> NutritionLogListResponse:
    """Retrieves paginated daily nutrition entries for a patient."""
    service = ClinicalService(db)
    return service.get_patient_nutrition(
        patient_id=patient_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/lifestyle",
    response_model=LifestyleLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log daily lifestyle & activity telemetry",
)
def log_daily_lifestyle(
    payload: LifestyleLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LifestyleLogRead:
    """Logs daily activity, step counts, sleep hours, and stress telemetry."""
    service = ClinicalService(db)
    return service.log_daily_lifestyle(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )


@router.get(
    "/lifestyle/patient/{patient_id}",
    response_model=LifestyleLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient lifestyle history",
)
def get_patient_lifestyle_history(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> LifestyleLogListResponse:
    """Retrieves paginated daily lifestyle telemetry history for a patient."""
    service = ClinicalService(db)
    return service.get_patient_lifestyle(
        patient_id=patient_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        page=page,
        page_size=page_size,
    )