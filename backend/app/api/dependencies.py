"""
API Security Dependencies.

Provides FastAPI dependency functions for extracting and verifying JWT tokens,
injecting authenticated user contexts, and enforcing RBAC/FGAC authorization guards.
"""

from typing import Annotated, List, Optional
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Import database session dependency
try:
    from app.db.session import get_db
except ImportError:
    from app.db.session import get_db

from app.db.models import User
from app.core.jwt import JWTEngine, TokenPayload
from app.core.exceptions import (
    AccountDisabledException,
    InsufficientPermissionError,
    TokenRevokedError,
)
from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.services.authorization_service import AuthorizationService
from app.schemas.auth_enums import Permission, TokenType, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)


def get_jwt_engine() -> JWTEngine:
    """Dependency provider for the application JWTEngine instance."""
    return JWTEngine(
        secret_key="SUPER_SECRET_PRODUCTION_KEY_REPLACE_IN_ENV",
        algorithm="HS256",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )


def get_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt_engine: Annotated[JWTEngine, Depends(get_jwt_engine)],
) -> TokenPayload:
    """
    Parses and verifies the OAuth2 Bearer Access Token.
    Returns decoded TokenPayload claims.
    """
    return jwt_engine.decode_token(token, expected_type=TokenType.ACCESS)


def get_current_user(
    payload: Annotated[TokenPayload, Depends(get_token_payload)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Resolves the authenticated User record from the database.
    Validates account state and session revocation.
    """
    if payload.sid:
        session_repo = SessionRepository(db)
        session = session_repo.get_active_session(payload.sid)
        if not session:
            raise TokenRevokedError("Associated session is no longer active.")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(payload.sub))

    if not user.is_active:
        raise AccountDisabledException()

    return user


class RequireRole:
    """
    Dependency callable guard that enforces Role-Based Access Control (RBAC).
    """

    def __init__(self, allowed_roles: List[UserRole] | UserRole) -> None:
        if isinstance(allowed_roles, UserRole):
            self.allowed_roles = [allowed_roles]
        else:
            self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in self.allowed_roles:
            raise InsufficientPermissionError(
                f"Required role in {[r.value for r in self.allowed_roles]}"
            )
        return current_user


class RequirePermission:
    """
    Dependency callable guard that enforces Fine-Grained Access Control (FGAC).
    """

    def __init__(self, required_permission: Permission) -> None:
        self.required_permission = required_permission

    def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> User:
        authz_service = AuthorizationService(db)
        if not authz_service.has_permission(current_user.role, self.required_permission):
            raise InsufficientPermissionError(self.required_permission.value)
        return current_user


def get_client_ip(request: Request) -> Optional[str]:
    """Helper dependency to extract client IP address handling reverse proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> Optional[str]:
    """Helper dependency to extract request User-Agent header."""
    return request.headers.get("User-Agent")