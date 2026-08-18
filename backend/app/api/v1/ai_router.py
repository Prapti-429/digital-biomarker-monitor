"""AI inference REST endpoints for longitudinal digital biomarkers."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.ai_schemas import AIAnalysisRequest, AIAnalysisResponse, AIHistoryResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Biomarker Inference"])


@router.post(
    "/analyze",
    response_model=AIAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze one multimodal daily monitoring session",
)
def analyze_session(
    payload: AIAnalysisRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AIAnalysisResponse:
    """Runs the personalized observational anomaly model for the authenticated user."""
    return AIService(db).analyze(current_user.id, payload)


@router.get(
    "/latest",
    response_model=AIAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the latest AI biomarker result",
)
def latest_result(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AIAnalysisResponse:
    result = AIService(db).latest(current_user.id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No AI analysis has been generated yet.")
    return result


@router.get(
    "/history",
    response_model=AIHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get longitudinal AI biomarker history",
)
def history(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=30, ge=1, le=100),
) -> AIHistoryResponse:
    return AIService(db).history(current_user.id, limit=limit)
