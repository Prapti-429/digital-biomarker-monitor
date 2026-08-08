"""
Administrative Oversight REST Router (/api/v1/admin).

Guarded endpoints for administrative user management and compliance audit review.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.api.dependencies import RequireRole
from app.services.audit_service import AuditService
from app.services.user_service import UserService
from app.schemas.auth_enums import UserRole
from app.schemas.audit_schemas import AuditLogListResponse
from app.schemas.user_schemas import UserAdminUpdate, UserListResponse, UserRead

router = APIRouter(
    prefix="/admin",
    tags=["Admin Management"],
    dependencies=[Depends(RequireRole([UserRole.ADMINISTRATOR, UserRole.ADMIN]))],
)


@router.get(
    "/users",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all platform users (Admin only)",
)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> UserListResponse:
    """Retrieves paginated platform user directory for administrators."""
    user_service = UserService(db)
    return user_service.admin_list_users(page=page, page_size=page_size)


@router.patch(
    "/users/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update user role or status (Admin only)",
)
def update_user_status(
    user_id: int,
    payload: UserAdminUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    """Updates user activation state, verification status, or role assignment."""
    user_service = UserService(db)
    return user_service.admin_update_user(user_id, payload)


@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="View system security audit logs (Admin only)",
)
def get_audit_logs(
    db: Annotated[Session, Depends(get_db)],
    user_id: int = Query(..., description="Target user ID to inspect logs"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> AuditLogListResponse:
    """Inspects immutable security audit logs for compliance auditing."""
    audit_service = AuditService(db)
    return audit_service.get_user_audit_logs(user_id=user_id, page=page, page_size=page_size)