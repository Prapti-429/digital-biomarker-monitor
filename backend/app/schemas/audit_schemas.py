"""
Security Audit Log Data Transfer Objects (DTOs).

Defines response structures for compliance auditing and security log queries.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class AuditLogRead(BaseModel):
    """Response contract for an individual audit log entry."""
    id: int
    user_id: Optional[int] = Field(None, description="ID of actor performing the action")
    actor_email: Optional[str] = Field(None, description="Email of actor performing the action")
    action: str = Field(..., description="System action name (e.g., LOGIN_SUCCESS)")
    resource_type: Optional[str] = Field(None, description="Target domain entity type")
    resource_id: Optional[str] = Field(None, description="Target entity ID")
    status: str = Field(..., description="Outcome status (SUCCESS/FAILURE)")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client User-Agent header")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Contextual JSON metadata")
    created_at: datetime = Field(..., description="Log creation UTC timestamp")

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Paginated list of audit logs."""
    items: list[AuditLogRead]
    total: int
    page: int
    page_size: int
    pages: int