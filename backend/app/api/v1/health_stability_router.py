"""
Health Stability Score REST API Router (/api/v1/health-stability).

Exposes multi-factor health stability scores, sub-dimension breakdowns,
and longitudinal trend points.
"""

from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

try:
    from app.database import get_db  # type: ignore[import-not-found]
except ImportError:
    from database import get_db  # type: ignore[import-not-found]

from app.db.models import User
from app.api.dependencies import get_current_user

try:
    from app.services.health_stability_service import HealthStabilityService
except ImportError:
    from services.health_stability_service import HealthStabilityService  # type: ignore[import-not-found]

from app.schemas.health_stability_schemas import HealthStabilityScoreRead

router = APIRouter(prefix="/health-stability", tags=["Health Stability Index"])


@router.get(
    "/patient/{patient_id}",
    response_model=HealthStabilityScoreRead,
    status_code=status.HTTP_200_OK,
    summary="Get patient Health Stability Score (HSS)",
)
def get_patient_health_stability_score(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> HealthStabilityScoreRead:
    """Calculates multi-dimensional composite Health Stability Score (0-100) and sub-system scores."""
    service = HealthStabilityService(db)
    return service.calculate_patient_hss(patient_id=patient_id)