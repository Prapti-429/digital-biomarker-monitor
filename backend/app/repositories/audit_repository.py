"""
Security Audit Log Repository.

Provides immutable persistence and filtering utilities for security and compliance audit records.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.audit_models import AuditLog
from app.repositories.base import BaseRepository, RepositoryError, PaginationParams, PaginatedResult, SortParam, SortOrder


class AuditLogRepository(BaseRepository[AuditLog, None, None]):
    """
    Repository for persisting and querying system Audit Logs.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(AuditLog, session)

    def log_event(
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
    ) -> AuditLog:
        """Persists an append-only security audit log entry."""
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                actor_email=actor_email,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                status=status,
                ip_address=ip_address,
                user_agent=user_agent,
                extra_data=extra_data,
            )
            self.session.add(audit_entry)
            self.session.commit()
            self.session.refresh(audit_entry)
            return audit_entry
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Failed to record audit log for action '{action}'", e)

    def get_logs_for_user(
        self, user_id: int, pagination: PaginationParams
    ) -> PaginatedResult[AuditLog]:
        """Fetches paginated audit logs associated with a specific user."""
        filters = {"user_id": user_id}
        sort_params = [SortParam(field="created_at", order=SortOrder.DESC)]
        return self.paginate(pagination=pagination, filters=filters, sort_params=sort_params)