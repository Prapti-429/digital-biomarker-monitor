"""
Audit Service.

Exposes clean application service interface for registering security events.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.audit_repository import AuditLogRepository
from app.schemas.audit_schemas import AuditLogRead, AuditLogListResponse
from app.repositories.base import PaginationParams


class AuditService:
    """
    Service responsible for handling security and compliance audit logging.
    """

    def __init__(self, db: Session) -> None:
        self.audit_repo = AuditLogRepository(db)

    def record_event(
        self,
        action: str,
        user_id: Optional[int] = None,
        actor_email: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Asynchronously or synchronously writes an audit entry."""
        self.audit_repo.log_event(
            action=action,
            user_id=user_id,
            actor_email=actor_email,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data,
        )

    def get_user_audit_logs(
        self, user_id: int, page: int = 1, page_size: int = 20
    ) -> AuditLogListResponse:
        """Queries audit logs for a specific user."""
        pagination = PaginationParams(page=page, page_size=page_size)
        result = self.audit_repo.get_logs_for_user(user_id, pagination)
        items = [AuditLogRead.model_validate(item) for item in result.items]
        return AuditLogListResponse(
            items=items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            pages=result.pages,
        )