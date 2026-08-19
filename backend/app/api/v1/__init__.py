"""API v1 router bundle."""
from fastapi import APIRouter
from app.api.v1.ai_router import router as ai_router
from app.api.v1.auth_router import router as auth_router
from app.api.v1.user_router import router as user_router
from app.api.v1.admin_router import router as admin_router
from app.api.v1.patient_router import router as patient_router
from app.api.v1.medication_router import router as medication_router
from app.api.v1.clinical_router import router as clinical_router
from app.api.v1.past_history_router import router as past_history_router
from app.api.v1.companion_router import router as companion_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(patient_router)
api_v1_router.include_router(medication_router)
api_v1_router.include_router(clinical_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(past_history_router)
api_v1_router.include_router(companion_router)

__all__ = ["api_v1_router"]
