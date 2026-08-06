"""
User Profile and Administration Data Transfer Objects (DTOs).

Defines validation and response contracts for user profiles, admin updates,
and RBAC role assignments.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.auth_enums import UserRole


class UserBase(BaseModel):
    """Base user attributes shared across schemas."""
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.PATIENT
    is_active: bool = True
    is_verified: bool = False


class UserRead(UserBase):
    """Public representation of a user account."""
    id: int = Field(..., description="Primary user ID")
    created_at: datetime = Field(..., description="Account creation UTC timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last successful login UTC timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    """Payload for self-service profile edits by the authenticated user."""
    full_name: Optional[str] = Field(None, max_length=255, description="Updated display name")


class UserAdminUpdate(BaseModel):
    """Payload for administrative updates to a user account."""
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserListResponse(BaseModel):
    """Paginated user list payload for admin operations."""
    items: List[UserRead]
    total: int
    page: int
    page_size: int
    pages: int