"""Conversational companion endpoint."""
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.companion_schemas import CompanionRequest, CompanionResponse
from app.services.companion_service import answer

router = APIRouter(prefix="/companion", tags=["AI Companion"])

@router.post("/chat", response_model=CompanionResponse)
def chat(
    payload: CompanionRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CompanionResponse:
    text, category, disclaimer = answer(payload.message, payload.language)
    return CompanionResponse(answer=text, category=category, disclaimer=disclaimer)
