"""Audit service for security/compliance events.

Audit logging must never turn an otherwise valid authentication operation into
an authentication failure. Persistence errors are logged and the primary
request is allowed to continue.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.audit_repository import AuditLogRepository
from app.schemas.audit_schemas import AuditLogRead, AuditLogListResponse
from app.repositories.base import PaginationParams, RepositoryError

logger = logging.getLogger(__name__)


class AuditService:
    """Service responsible for security/compliance audit events."""

    def __init__(self, db: Session) -> None:
        self.audit_repo = AuditLogRepository(db)

    def record_event(
        self,
        action: str,
        user_id: Optional[UUID] = None,
        actor_email: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Write an audit event without making the primary operation fail.

        Authentication, registration, and logout must not be reported to the
        user as failures merely because audit persistence is temporarily
        unavailable. The failure is retained in server logs for diagnosis.
        """
        try:
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
        except RepositoryError:
            logger.exception("Audit event could not be persisted: %s", action)

    def get_user_audit_logs(
        self, user_id: UUID, page: int = 1, page_size: int = 20
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
