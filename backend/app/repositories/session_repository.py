"""
Session and Refresh Token Repository.

Provides thread-safe data operations for managing user sessions, device tracking,
and token rotation/revocation logic.
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.auth_models import UserSession, RefreshToken
from app.repositories.base import BaseRepository, RepositoryError, EntityNotFoundError


class SessionRepository(BaseRepository[UserSession, None, None]):
    """
    Repository for managing UserSession entities and bound Refresh Tokens.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(UserSession, session)

    def create_session(
        self,
        user_id: int,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
    ) -> UserSession:
        """Establishes a new active user session."""
        try:
            db_session = UserSession(
                user_id=user_id,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                is_revoked=False,
            )
            self.session.add(db_session)
            self.session.commit()
            self.session.refresh(db_session)
            return db_session
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Failed to establish session for user {user_id}", e)

    def get_active_session(self, session_id: str) -> Optional[UserSession]:
        """Retrieves a valid, non-revoked session by ID."""
        try:
            stmt = select(UserSession).where(
                UserSession.id == session_id,
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.now(timezone.utc),
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error querying active session {session_id}", e)

    def revoke_session(self, session_id: str) -> bool:
        """Revokes a user session and all associated refresh tokens."""
        try:
            db_session = self.get_by_id(session_id)
            db_session.is_revoked = True
            
            # Also revoke bound refresh tokens
            stmt = (
                update(RefreshToken)
                .where(RefreshToken.session_id == session_id)
                .values(is_revoked=True, revoked_at=datetime.now(timezone.utc))
            )
            self.session.execute(stmt)
            self.session.commit()
            return True
        except EntityNotFoundError:
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Failed to revoke session {session_id}", e)

    def revoke_all_user_sessions(self, user_id: int) -> int:
        """Revokes all active sessions for a user (e.g. on password change or admin override)."""
        try:
            now = datetime.now(timezone.utc)
            # Revoke sessions
            stmt_sessions = (
                update(UserSession)
                .where(UserSession.user_id == user_id, UserSession.is_revoked == False)
                .values(is_revoked=True)
            )
            res = self.session.execute(stmt_sessions)
            
            # Revoke all refresh tokens
            stmt_tokens = (
                update(RefreshToken)
                .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
                .values(is_revoked=True, revoked_at=now)
            )
            self.session.execute(stmt_tokens)
            
            self.session.commit()
            return res.rowcount
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Error revoking sessions for user {user_id}", e)

    # -------------------------------------------------------------------------
    # REFRESH TOKEN METHODS
    # -------------------------------------------------------------------------

    def create_refresh_token(
        self,
        jti: str,
        session_id: str,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        parent_token_id: Optional[str] = None,
    ) -> RefreshToken:
        """Records an issued Refresh Token in the database registry."""
        try:
            db_token = RefreshToken(
                jti=jti,
                session_id=session_id,
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
                parent_token_id=parent_token_id,
                is_revoked=False,
            )
            self.session.add(db_token)
            self.session.commit()
            self.session.refresh(db_token)
            return db_token
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError("Failed to store refresh token in database", e)

    def get_refresh_token_by_jti(self, jti: str) -> Optional[RefreshToken]:
        """Fetches a refresh token record by its unique JTI."""
        try:
            stmt = select(RefreshToken).where(RefreshToken.jti == jti)
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to query refresh token JTI {jti}", e)

    def revoke_refresh_token(self, jti: str) -> bool:
        """Marks a specific refresh token as revoked."""
        try:
            token = self.get_refresh_token_by_jti(jti)
            if not token:
                return False
            token.is_revoked = True
            token.revoked_at = datetime.now(timezone.utc)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Failed to revoke refresh token {jti}", e)