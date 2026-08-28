"""Conversational companion endpoint."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.db.models import User
from app.schemas.companion_schemas import CompanionRequest, CompanionResponse
from app.services.companion_service import answer

router = APIRouter(prefix="/companion", tags=["AI Companion"])


@router.post("/chat", response_model=CompanionResponse)
def chat(
    payload: CompanionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> CompanionResponse:
    """Answer a companion question without requiring a database session.

    The companion only needs the authenticated identity; the deterministic
    safety-first answer engine does not read or write database state. Keeping
    the endpoint independent of the DB prevents an unrelated database hiccup
    from surfacing to the user as a generic companion network error.
    """
    message = (payload.message or "").strip()
    if not message:
        return CompanionResponse(
            answer="Please enter a question so I can help explain NUVYRA.",
            category="system",
            disclaimer=(
                "NUVYRA is a research platform. Its digital-biomarker features "
                "are experimental and are not clinically validated or a diagnosis."
            ),
        )

    text, category, disclaimer = answer(message, payload.language)
    return CompanionResponse(answer=text, category=category, disclaimer=disclaimer)
