"""
Role and Permission Repository.

Handles relational RBAC lookup, role assignment, and permission resolution.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.auth_models import Role, Permission
from app.repositories.base import BaseRepository, RepositoryError


class RoleRepository(BaseRepository[Role, None, None]):
    """
    Repository layer for managing RBAC roles and permissions.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(Role, session)

    def get_by_name(self, name: str) -> Optional[Role]:
        """Fetches a Role by its unique name (e.g. 'administrator', 'patient')."""
        try:
            stmt = (
                select(Role)
                .where(Role.name == name.lower().strip())
                .options(selectinload(Role.permissions))
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to fetch role '{name}'", e)

    def get_permission_codes_for_role(self, role_name: str) -> List[str]:
        """Resolves all granular permission code strings associated with a role."""
        role = self.get_by_name(role_name)
        if not role:
            return []
        return [perm.code for perm in role.permissions]