"""
API Package Initialization.
Exports root API router incorporating all versioned routes.
"""

from fastapi import APIRouter
from app.api.v1 import api_v1_router

root_api_router = APIRouter(prefix="/api")
root_api_router.include_router(api_v1_router)