"""User profile DTOs."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.auth_enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.PATIENT
    is_active: bool = True
    is_verified: bool = False


class UserRead(UserBase):
    id: UUID = Field(..., description="Primary user UUID")
    created_at: datetime
    last_login_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)


class UserAdminUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserListResponse(BaseModel):
    items: List[UserRead]
    total: int
    page: int
    page_size: int
    pages: int
