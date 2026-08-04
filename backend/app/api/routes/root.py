"""
Root V1 API Routes.

Exposes informational endpoints for API v1 namespace discovery.
"""

from typing import Any, Dict
from fastapi import APIRouter, status

from app.core.config import settings

router = APIRouter(tags=["API Discovery"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="API v1 Information",
    description="Returns base configuration metadata for the v1 API namespace.",
)
def get_v1_info() -> Dict[str, Any]:
    """
    Returns system discovery info for the API v1 namespace.

    Returns:
        Dict[str, Any]: System configuration details.
    """
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_version": "v1",
        "database_backend": "PostgreSQL",
    }