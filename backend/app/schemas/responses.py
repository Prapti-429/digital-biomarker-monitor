"""Standardized API response models."""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class ErrorDetail(BaseModel):
    """Detailed error structure."""
    code: str = Field(..., description="Application-specific error code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[Any] = Field(None, description="Additional context, like validation fields")

class StandardResponse(BaseModel, Generic[T]):
    """
    Standard JSend-like wrapper for all successful API responses.
    """
    success: bool = Field(default=True)
    message: str = Field(default="Success")
    data: Optional[T] = Field(default=None)
    meta: Optional[dict[str, Any]] = Field(default=None, description="Pagination or request metadata")

class ErrorResponse(BaseModel):
    """
    Standard wrapper for all API errors.
    """
    success: bool = Field(default=False)
    error: ErrorDetail
    path: str = Field(..., description="The URL path where the error occurred")