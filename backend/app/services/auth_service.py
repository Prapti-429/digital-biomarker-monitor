"""Authentication service for registration, login, refresh rotation and logout."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import InvalidCredentialsException, AccountLockedException, AccountDisabledException, InvalidTokenError, TokenRevokedError
from app.core.jwt import JWTEngine
from app.core.security import hash_password, verify_password
from app.db.models import User
from app.repositories.base import DuplicateEntityError
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.authorization_service import AuthorizationService
from app.schemas.auth_enums import TokenType
from app.schemas.auth_schemas import LoginRequest, TokenResponse, UserRegisterRequest

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class AuthenticationService:
    def __init__(self, db: Session, jwt_engine: JWTEngine) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
        self.authz_service = AuthorizationService(db)
        self.audit_service = AuditService(db)
        self.jwt_engine = jwt_engine

    def register_user(self, payload: UserRegisterRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> User:
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise DuplicateEntityError("User", f"Email '{payload.email}' is already registered.")
        user = self.user_repo.create_user({
            "email": payload.email.lower().strip(),
            "hashed_password": hash_password(payload.password),
            "full_name": payload.full_name,
            "role": payload.role,
            "is_active": True,
            "is_verified": False,
        })
        self.audit_service.record_event(action="USER_REGISTER", user_id=user.id, actor_email=user.email, status="SUCCESS", ip_address=ip_address, user_agent=user_agent)
        return user

    def authenticate_user(self, payload: LoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        user = self.user_repo.get_by_email(payload.email)
        if not user:
            self.audit_service.record_event(action="LOGIN_FAILED", actor_email=payload.email, status="FAILURE", ip_address=ip_address, user_agent=user_agent, extra_data={"reason": "User not found"})
            raise InvalidCredentialsException()
        now = datetime.now(timezone.utc)
        if user.locked_until and user.locked_until > now:
            raise AccountLockedException(f"Account is locked until {user.locked_until.isoformat()} UTC.")
        if not user.is_active:
            raise AccountDisabledException()
        if not verify_password(payload.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            self.db.commit()
            self.audit_service.record_event(action="LOGIN_FAILED", user_id=user.id, actor_email=user.email, status="FAILURE", ip_address=ip_address, user_agent=user_agent, extra_data={"attempts": user.failed_login_attempts})
            raise InvalidCredentialsException()

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now
        self.db.commit()

        session_expiry = now + timedelta(days=self.jwt_engine.refresh_token_expire_days)
        session = self.session_repo.create_session(user_id=user.id, expires_at=session_expiry, ip_address=ip_address, user_agent=user_agent, device_fingerprint=payload.device_fingerprint)
        permissions = self.authz_service.get_user_permissions(user.role)
        access_token, _ = self.jwt_engine.create_access_token(subject=str(user.id), role=user.role, permissions=permissions, session_id=session.id)
        refresh_token, ref_payload = self.jwt_engine.create_refresh_token(subject=str(user.id), role=user.role, session_id=session.id)
        self.session_repo.create_refresh_token(jti=ref_payload.jti, session_id=session.id, user_id=user.id, token_hash=hashlib.sha256(refresh_token.encode()).hexdigest(), expires_at=ref_payload.exp)
        self.audit_service.record_event(action="LOGIN_SUCCESS", user_id=user.id, actor_email=user.email, status="SUCCESS", ip_address=ip_address, user_agent=user_agent)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="Bearer", expires_in=self.jwt_engine.access_token_expire_minutes * 60)

    def refresh_tokens(self, raw_refresh_token: str) -> TokenResponse:
        payload = self.jwt_engine.decode_token(raw_refresh_token, expected_type=TokenType.REFRESH)
        if not payload.sid:
            raise InvalidTokenError("Refresh token missing session context.")
        session = self.session_repo.get_active_session(payload.sid)
        if not session:
            raise TokenRevokedError("Associated session is revoked or expired.")
        ref_record = self.session_repo.get_refresh_token_by_jti(payload.jti)
        if not ref_record or ref_record.is_revoked:
            self.session_repo.revoke_session(payload.sid)
            raise TokenRevokedError("Token reuse detected. Session terminated.")
        self.session_repo.revoke_refresh_token(payload.jti)
        try:
            user_id = UUID(str(payload.sub))
        except ValueError as exc:
            raise InvalidTokenError("Refresh token contains an invalid user identifier.") from exc
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidTokenError("User account is unavailable.")
        permissions = self.authz_service.get_user_permissions(user.role)
        new_access_token, _ = self.jwt_engine.create_access_token(subject=str(user.id), role=user.role, permissions=permissions, session_id=session.id)
        new_refresh_token, new_payload = self.jwt_engine.create_refresh_token(subject=str(user.id), role=user.role, session_id=session.id)
        self.session_repo.create_refresh_token(jti=new_payload.jti, session_id=session.id, user_id=user.id, token_hash=hashlib.sha256(new_refresh_token.encode()).hexdigest(), expires_at=new_payload.exp, parent_token_id=ref_record.id)
        return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, token_type="Bearer", expires_in=self.jwt_engine.access_token_expire_minutes * 60)

    def logout(self, session_id: str, user_id: UUID) -> bool:
        revoked = self.session_repo.revoke_session(session_id)
        if revoked:
            self.audit_service.record_event(action="LOGOUT", user_id=user_id, status="SUCCESS")
        return revoked
