"""
User Repository handling authentication lookup, registration, 
and user account lifecycle operations.
"""

from typing import Optional, Any, Dict
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import User
from app.repositories.base import BaseRepository, EntityNotFoundError, RepositoryError


class UserRepository(BaseRepository[User, Any, Any]):
    """
    Repository layer for User domain model.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(User, session)

    def create_user(self, user_data: Dict[str, Any], auto_commit: bool = True) -> User:
        """
        Create a new system user record.
        """
        return self.create(obj_in=user_data, auto_commit=auto_commit)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Find a active user by their email address.
        """
        try:
            stmt = select(User).where(User.email == email.strip().lower())
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to query user by email '{email}'", e)

    def get_by_uuid(self, uuid_val: str) -> Optional[User]:
        """
        Retrieve a user record by UUID (e.g., Supabase Auth UID mapping).
        """
        try:
            if hasattr(User, "uuid"):
                stmt = select(User).where(getattr(User, "uuid") == uuid_val)
                return self.session.execute(stmt).scalar_one_or_none()
            return self.get_by_id(uuid_val)
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve user by UUID '{uuid_val}'", e)

    def update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> User:
        """
        Update user metadata and demographic profile attributes.
        """
        return self.update(id_val=user_id, obj_in=profile_data, auto_commit=True)

    def deactivate_user(self, user_id: int) -> User:
        """
        Set user active status to False without deleting record.
        """
        try:
            user = self.get_by_id(user_id)
            user.is_active = False
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Failed to deactivate user ID {user_id}", e)

    def reactivate_user(self, user_id: int) -> User:
        """
        Reactivate a deactivated user account.
        """
        try:
            user = self.get_by_id(user_id)
            user.is_active = True
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Failed to reactivate user ID {user_id}", e)