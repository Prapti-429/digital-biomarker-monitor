"""
API v1 Router Bundle Package Initialization.

Aggregates and registers all versioned REST domain routers:
- /api/v1/auth
- /api/v1/users
- /api/v1/admin
- /api/v1/patients
- /api/v1/medications
- /api/v1/clinical
"""

from fastapi import APIRouter

from app.api.v1.auth_router import router as auth_router
from app.api.v1.user_router import router as user_router
from app.api.v1.admin_router import router as admin_router
from app.api.v1.patient_router import router as patient_router
from app.api.v1.medication_router import router as medication_router
from app.api.v1.clinical_router import router as clinical_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(patient_router)
api_v1_router.include_router(medication_router)
api_v1_router.include_router(clinical_router)

__all__ = ["api_v1_router"]