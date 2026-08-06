"""
Authorization Service.

Encapsulates role and permission checks for fine-grained access control (FGAC).
"""

from typing import List
from sqlalchemy.orm import Session

from app.repositories.role_repository import RoleRepository
from app.schemas.auth_enums import UserRole, Permission


class AuthorizationService:
    """
    Service responsible for enforcing Role-Based and Permission-Based authorization rules.
    """

    def __init__(self, db: Session) -> None:
        self.role_repo = RoleRepository(db)

    def get_user_permissions(self, role: UserRole) -> List[str]:
        """Resolves list of granted permission strings for a given role."""
        return self.role_repo.get_permission_codes_for_role(role.value)

    def has_permission(self, role: UserRole, required_permission: Permission) -> bool:
        """Checks if a given role possesses a required granular permission."""
        permissions = self.get_user_permissions(role)
        return required_permission.value in permissions