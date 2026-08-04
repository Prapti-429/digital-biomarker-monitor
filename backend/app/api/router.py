"""
Central API Router.

Consolidates and mounts all sub-routers and endpoint groups for API v1.
"""

from fastapi import APIRouter

from app.api.routes import health, root

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(root.router)
api_router.include_router(health.router)