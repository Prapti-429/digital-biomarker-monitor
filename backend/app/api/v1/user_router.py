"""
User Self-Management REST Router (/api/v1/users).

Allows authenticated users to view and update their profile and credentials.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

try:
    from app.db.session import get_db
except ImportError:
    from app.db.session import get_db

from app.db.models import User
from app.core.security import verify_password, hash_password
from app.core.exceptions import InvalidCredentialsException
from app.api.dependencies import get_current_user
from app.services.user_service import UserService
from app.schemas.auth_schemas import ChangePasswordRequest
from app.schemas.user_schemas import UserProfileUpdate, UserRead

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get(
    "/profile",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="View authenticated user profile",
)
def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Returns detailed user account profile information."""
    return UserRead.model_validate(current_user)


@router.patch(
    "/profile",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update profile details",
)
def update_profile(
    payload: UserProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    """Updates profile attributes for the authenticated user."""
    user_service = UserService(db)
    return user_service.update_profile(current_user.id, payload)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change account password",
)
def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Verifies existing password and updates to candidate replacement password."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise InvalidCredentialsException("Current password verification failed.")

    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"detail": "Password changed successfully."}