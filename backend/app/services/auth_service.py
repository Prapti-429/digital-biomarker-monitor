"""
Authentication Service.

Orchestrates credential verification, account lockout policies, session binding,
and JWT access/refresh token issuance and rotation.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.db.models import User
from app.core.security import hash_password, verify_password
from app.core.jwt import JWTEngine, TokenPayload
from app.core.exceptions import (
    InvalidCredentialsException,
    AccountLockedException,
    AccountDisabledException,
    InvalidTokenError,
    TokenRevokedError,
    DuplicateEntityError,
)
from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.services.authorization_service import AuthorizationService
from app.services.audit_service import AuditService
from app.schemas.auth_schemas import UserRegisterRequest, LoginRequest, TokenResponse
from app.schemas.auth_enums import TokenType, UserRole


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class AuthenticationService:
    """
    Central service handling identity authentication and credential security.
    """

    def __init__(self, db: Session, jwt_engine: JWTEngine) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
        self.authz_service = AuthorizationService(db)
        self.audit_service = AuditService(db)
        self.jwt_engine = jwt_engine

    def register_user(
        self,
        payload: UserRegisterRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        """Registers a new user account with hashed password."""
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise DuplicateEntityError("User", f"Email '{payload.email}' is already registered.")

        hashed_pwd = hash_password(payload.password)
        user_data = {
            "email": payload.email.lower().strip(),
            "hashed_password": hashed_pwd,
            "full_name": payload.full_name,
            "role": payload.role,
            "is_active": True,
            "is_verified": False,
        }

        user = self.user_repo.create_user(user_data)

        self.audit_service.record_event(
            action="USER_REGISTER",
            user_id=user.id,
            actor_email=user.email,
            status="SUCCESS",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return user

    def authenticate_user(
        self,
        payload: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """
        Verifies credentials, enforces lockout policy, establishes session, and issues JWT pair.
        """
        user = self.user_repo.get_by_email(payload.email)
        if not user:
            self.audit_service.record_event(
                action="LOGIN_FAILED",
                actor_email=payload.email,
                status="FAILURE",
                ip_address=ip_address,
                user_agent=user_agent,
                extra_data={"reason": "User not found"},
            )
            raise InvalidCredentialsException()

        now = datetime.now(timezone.utc)

        # Check account lock state
        if user.locked_until and user.locked_until > now:
            raise AccountLockedException(
                f"Account is locked until {user.locked_until.isoformat()} UTC."
            )

        # Check account activation
        if not user.is_active:
            raise AccountDisabledException()

        # Verify password
        if not verify_password(payload.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                self.audit_service.record_event(
                    action="ACCOUNT_LOCKED",
                    user_id=user.id,
                    actor_email=user.email,
                    status="WARNING",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

            self.user_repo.session.commit()

            self.audit_service.record_event(
                action="LOGIN_FAILED",
                user_id=user.id,
                actor_email=user.email,
                status="FAILURE",
                ip_address=ip_address,
                user_agent=user_agent,
                extra_data={"attempts": user.failed_login_attempts},
            )
            raise InvalidCredentialsException()

        # Successful Login -> Reset lockout counters
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now
        self.user_repo.session.commit()

        # Create active UserSession
        session_expiry = now + timedelta(days=self.jwt_engine.refresh_token_expire_days)
        session = self.session_repo.create_session(
            user_id=user.id,
            expires_at=session_expiry,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=payload.device_fingerprint,
        )

        # Generate JWT Tokens
        permissions = self.authz_service.get_user_permissions(user.role)
        access_token, _ = self.jwt_engine.create_access_token(
            subject=str(user.id),
            role=user.role,
            permissions=permissions,
            session_id=session.id,
        )

        refresh_token, ref_payload = self.jwt_engine.create_refresh_token(
            subject=str(user.id),
            role=user.role,
            session_id=session.id,
        )

        # Record Refresh Token in Registry
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        self.session_repo.create_refresh_token(
            jti=ref_payload.jti,
            session_id=session.id,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=ref_payload.exp,
        )

        self.audit_service.record_event(
            action="LOGIN_SUCCESS",
            user_id=user.id,
            actor_email=user.email,
            status="SUCCESS",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        expires_in = self.jwt_engine.access_token_expire_minutes * 60
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
        )

    def refresh_tokens(self, raw_refresh_token: str) -> TokenResponse:
        """
        Validates refresh token, checks revocation status, rotates token, and issues new pair.
        """
        payload = self.jwt_engine.decode_token(raw_refresh_token, expected_type=TokenType.REFRESH)
        
        # Verify Session
        if not payload.sid:
            raise InvalidTokenError("Refresh token missing session context.")

        session = self.session_repo.get_active_session(payload.sid)
        if not session:
            raise TokenRevokedError("Associated session is revoked or expired.")

        # Verify Refresh Token Registry
        ref_record = self.session_repo.get_refresh_token_by_jti(payload.jti)
        if not ref_record or ref_record.is_revoked:
            # Token Reuse Attack Detected -> Revoke entire session
            self.session_repo.revoke_session(payload.sid)
            raise TokenRevokedError("Token reuse detected. Session terminated.")

        # Revoke current refresh token (Rotation)
        self.session_repo.revoke_refresh_token(payload.jti)

        user = self.user_repo.get_by_id(int(payload.sub))
        permissions = self.authz_service.get_user_permissions(user.role)

        # Issue new Access & Refresh tokens
        new_access_token, _ = self.jwt_engine.create_access_token(
            subject=str(user.id),
            role=user.role,
            permissions=permissions,
            session_id=session.id,
        )

        new_refresh_token, new_ref_payload = self.jwt_engine.create_refresh_token(
            subject=str(user.id),
            role=user.role,
            session_id=session.id,
        )

        new_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
        self.session_repo.create_refresh_token(
            jti=new_ref_payload.jti,
            session_id=session.id,
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=new_ref_payload.exp,
            parent_token_id=ref_record.id,
        )

        expires_in = self.jwt_engine.access_token_expire_minutes * 60
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
        )

    def logout(self, session_id: str, user_id: int) -> bool:
        """Revokes session and terminates active access."""
        revoked = self.session_repo.revoke_session(session_id)
        if revoked:
            self.audit_service.record_event(
                action="LOGOUT",
                user_id=user_id,
                status="SUCCESS",
            )
        return revoked