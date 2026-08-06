"""
User Management Service.

Handles user profile updates, deactivation/reactivation, and admin queries.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserRead, UserProfileUpdate, UserAdminUpdate, UserListResponse
from app.repositories.base import PaginationParams, EntityNotFoundError
from app.core.exceptions import AccountDisabledException


class UserService:
    """
    Service managing user profile lifecycles and administrative actions.
    """

    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> UserRead:
        """Retrieves user by ID and returns safe Read DTO."""
        user = self.user_repo.get_by_id(user_id)
        return UserRead.model_validate(user)

    def update_profile(self, user_id: int, payload: UserProfileUpdate) -> UserRead:
        """Updates display name or profile details for the authenticated user."""
        data = payload.model_dump(exclude_unset=True)
        updated_user = self.user_repo.update_profile(user_id, data)
        return UserRead.model_validate(updated_user)

    def admin_update_user(self, target_user_id: int, payload: UserAdminUpdate) -> UserRead:
        """Executes administrative updates (role shifts, activation toggles)."""
        data = payload.model_dump(exclude_unset=True)
        updated_user = self.user_repo.update(target_user_id, data)
        return UserRead.model_validate(updated_user)

    def admin_list_users(self, page: int = 1, page_size: int = 20) -> UserListResponse:
        """Retrieves paginated user directory for administrators."""
        pagination = PaginationParams(page=page, page_size=page_size)
        res = self.user_repo.paginate(pagination=pagination)
        items = [UserRead.model_validate(item) for item in res.items]
        return UserListResponse(
            items=items,
            total=res.total,
            page=res.page,
            page_size=res.page_size,
            pages=res.pages,
        )