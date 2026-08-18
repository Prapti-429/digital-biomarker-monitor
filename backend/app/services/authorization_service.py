"""Authorization service for role and permission checks."""

from typing import List, Union

from sqlalchemy.orm import Session

from app.repositories.role_repository import RoleRepository
from app.schemas.auth_enums import UserRole, Permission


class AuthorizationService:
    """Encapsulates RBAC and permission resolution."""

    def __init__(self, db: Session) -> None:
        self.role_repo = RoleRepository(db)

    @staticmethod
    def _role_value(role: Union[UserRole, str]) -> str:
        return role.value if isinstance(role, UserRole) else str(role)

    def get_user_permissions(self, role: Union[UserRole, str]) -> List[str]:
        """Resolve granular permission codes for either enum or persisted string roles."""
        return self.role_repo.get_permission_codes_for_role(self._role_value(role))

    def has_permission(self, role: Union[UserRole, str], required_permission: Permission) -> bool:
        """Check whether a role has the requested permission."""
        permissions = self.get_user_permissions(role)
        return required_permission.value in permissions
