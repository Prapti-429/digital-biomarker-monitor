"""
Nutrition REST API Router (/api/v1/nutrition).

Exposes endpoints for meal intake telemetry, historical queries, and automated
rule-based nutritional recommendations.
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
from app.api.dependencies import get_current_user, get_client_ip

try:
    from app.services.clinical_service import ClinicalService
    from app.services.nutrition_engine import NutritionRecommendationEngine
except ImportError:
    from services.clinical_service import ClinicalService  # type: ignore[import-not-found]
    from services.nutrition_engine import NutritionRecommendationEngine  # type: ignore[import-not-found]

from app.schemas.nutrition_schemas import (
    NutritionLogCreate,
    NutritionLogRead,
    NutritionLogListResponse,
    NutritionRecommendationResponse,
)

router = APIRouter(prefix="/nutrition", tags=["Nutrition Telemetry & Recommendations"])


@router.post(
    "",
    response_model=NutritionLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log daily nutrition intake",
)
def log_daily_nutrition(
    payload: NutritionLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NutritionLogRead:
    """Logs daily nutrition intake, fluid balance, and meal tolerance notes."""
    service = ClinicalService(db)
    log_entry = service.log_daily_nutrition(
        schema=payload,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )
    return NutritionLogRead.model_validate(log_entry)


@router.get(
    "/patient/{patient_id}",
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
    """Retrieves paginated historical nutrition entries for a patient."""
    service = ClinicalService(db)
    return service.get_patient_nutrition(
        patient_id=patient_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/recommendations/patient/{patient_id}",
    response_model=NutritionRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get automated evidence-based nutrition recommendations",
)
def get_nutrition_recommendations(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NutritionRecommendationResponse:
    """Evaluates recent nutrition telemetry and prescribed TKI therapy to emit non-diagnostic recommendations."""
    engine = NutritionRecommendationEngine(db)
    return engine.generate_recommendations(patient_id=patient_id)