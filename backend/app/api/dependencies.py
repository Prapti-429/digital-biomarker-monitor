"""
API Security Dependencies.

Provides FastAPI dependency functions for extracting and verifying JWT tokens,
injecting authenticated user contexts, and enforcing RBAC/FGAC authorization guards.
"""

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.core.config import settings
from app.core.jwt import JWTEngine, TokenPayload
from app.core.exceptions import AccountDisabledException, InsufficientPermissionError, TokenRevokedError
from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.services.authorization_service import AuthorizationService
from app.schemas.auth_enums import Permission, TokenType, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)


def get_jwt_engine() -> JWTEngine:
    """Dependency provider for the application JWTEngine instance."""
    return JWTEngine(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )


def get_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt_engine: Annotated[JWTEngine, Depends(get_jwt_engine)],
) -> TokenPayload:
    """Parse and verify the OAuth2 Bearer access token."""
    return jwt_engine.decode_token(token, expected_type=TokenType.ACCESS)


def get_current_user(
    payload: Annotated[TokenPayload, Depends(get_token_payload)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve and validate the authenticated user from the JWT subject UUID."""
    if payload.sid:
        session = SessionRepository(db).get_active_session(payload.sid)
        if not session:
            raise TokenRevokedError("Associated session is no longer active.")

    try:
        user_id = UUID(str(payload.sub))
    except (ValueError, TypeError) as exc:
        raise TokenRevokedError("Token contains an invalid user identifier.") from exc

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise TokenRevokedError("Authenticated user no longer exists.")
    if not user.is_active:
        raise AccountDisabledException()
    return user


class RequireRole:
    """Dependency callable guard that enforces Role-Based Access Control."""

    def __init__(self, allowed_roles: List[UserRole] | UserRole) -> None:
        self.allowed_roles = [allowed_roles] if isinstance(allowed_roles, UserRole) else allowed_roles

    def __call__(self, current_user: Annotated[User, Depends(get_current_user)]) -> User:
        allowed_values = {role.value if isinstance(role, UserRole) else str(role) for role in self.allowed_roles}
        if str(current_user.role) not in allowed_values:
            raise InsufficientPermissionError(f"Required role in {sorted(allowed_values)}")
        return current_user


class RequirePermission:
    """Dependency callable guard that enforces Fine-Grained Access Control."""

    def __init__(self, required_permission: Permission) -> None:
        self.required_permission = required_permission

    def __call__(self, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> User:
        authz_service = AuthorizationService(db)
        if not authz_service.has_permission(current_user.role, self.required_permission):
            raise InsufficientPermissionError(self.required_permission.value)
        return current_user


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address while handling reverse proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> Optional[str]:
    """Extract request User-Agent header."""
    return request.headers.get("User-Agent")
