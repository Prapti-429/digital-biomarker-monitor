"""
Central API Router.

Consolidates and mounts all sub-routers and endpoint groups for API v1.
"""

from fastapi import APIRouter

from app.api.routes import health, root
from app.api.v1 import api_v1_router

api_router = APIRouter()

# Base/system endpoints
api_router.include_router(root.router)
api_router.include_router(health.router)

# Versioned application API (/api/v1/*)
api_router.include_router(api_v1_router)
