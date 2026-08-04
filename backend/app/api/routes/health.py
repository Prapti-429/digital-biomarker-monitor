"""
Health Probe API Routes.

Exposes system and database health check endpoints for container orchestrators,
monitoring tools, and manual verification.
"""

from typing import Any, Dict
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.db.health import check_db_health

router = APIRouter(prefix="/health", tags=["Infrastructure Health"])


class HealthResponseSchema(BaseModel):
    """
    Schema for health check endpoint responses.
    """

    status: str = Field(..., description="Overall status of application and services")
    project_name: str = Field(..., description="Name of the application project")
    version: str = Field(..., description="Application version")
    database: Dict[str, Any] = Field(..., description="Detailed status of database infrastructure")


@router.get(
    "",
    response_model=HealthResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Application & Database Health Probe",
    description="Performs active ping against PostgreSQL database and returns connection latency.",
)
def get_health_status() -> Dict[str, Any]:
    """
    Executes database connection verification and returns consolidated system health report.

    Returns:
        Dict[str, Any]: Application metadata and database health telemetry.
    """
    db_health = check_db_health()
    overall_status = "ok" if db_health.get("status") == "healthy" else "degraded"

    return {
        "status": overall_status,
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_health,
    }