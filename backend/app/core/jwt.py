"""
JSON Web Token (JWT) Cryptographic Engine.

Handles asymmetric/symmetric signed JWT generation, state validation, and claims
deserialization for Access, Refresh, Password Reset, and Verification tokens.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from pydantic import BaseModel, Field

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.schemas.auth_enums import TokenType, UserRole


class TokenPayload(BaseModel):
    """Structured JWT token claims payload."""
    sub: str = Field(..., description="Subject identifier (User ID / UUID)")
    jti: str = Field(..., description="Unique JWT Token Identifier for revocation tracking")
    sid: Optional[str] = Field(None, description="User Session Identifier")
    type: TokenType = Field(..., description="Category of token (access, refresh, etc.)")
    role: UserRole = Field(..., description="User primary role")
    permissions: list[str] = Field(default_factory=list, description="Assigned granular permissions")
    exp: datetime = Field(..., description="Expiration UTC timestamp")
    iat: datetime = Field(..., description="Issued-at UTC timestamp")
    iss: str = Field(default="digital-biomarker-platform", description="Token Issuer")


class JWTEngine:
    """
    Cryptographic manager for signing and parsing JWT tokens.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
        issuer: str = "digital-biomarker-platform",
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.issuer = issuer

    def create_access_token(
        self,
        subject: str,
        role: UserRole,
        permissions: list[str],
        session_id: Optional[str] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, TokenPayload]:
        """
        Generates a short-lived Access Token.
        """
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self.access_token_expire_minutes)
        jti = str(uuid.uuid4())

        payload = TokenPayload(
            sub=subject,
            jti=jti,
            sid=session_id,
            type=TokenType.ACCESS,
            role=role,
            permissions=permissions,
            exp=expires,
            iat=now,
            iss=self.issuer,
        )

        claims = payload.model_dump()
        if custom_claims:
            claims.update(custom_claims)

        # Convert datetimes to Unix timestamps for JWT encoding
        claims["exp"] = int(expires.timestamp())
        claims["iat"] = int(now.timestamp())

        encoded_jwt = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, payload

    def create_refresh_token(
        self,
        subject: str,
        role: UserRole,
        session_id: str,
    ) -> tuple[str, TokenPayload]:
        """
        Generates a long-lived Refresh Token bound to a Session ID.
        """
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=self.refresh_token_expire_days)
        jti = str(uuid.uuid4())

        payload = TokenPayload(
            sub=subject,
            jti=jti,
            sid=session_id,
            type=TokenType.REFRESH,
            role=role,
            permissions=[],
            exp=expires,
            iat=now,
            iss=self.issuer,
        )

        claims = payload.model_dump()
        claims["exp"] = int(expires.timestamp())
        claims["iat"] = int(now.timestamp())

        encoded_jwt = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, payload

    def decode_token(self, token: str, expected_type: Optional[TokenType] = None) -> TokenPayload:
        """
        Decodes, cryptographically verifies, and deserializes a JWT token string.
        
        Raises:
            TokenExpiredError: If token has passed exp timestamp.
            InvalidTokenError: If signature, claims, or payload is invalid.
        """
        try:
            raw_payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                options={"verify_iss": True, "verify_exp": True},
            )
            
            # Convert integer timestamps back to datetime objects
            raw_payload["exp"] = datetime.fromtimestamp(raw_payload["exp"], tz=timezone.utc)
            raw_payload["iat"] = datetime.fromtimestamp(raw_payload["iat"], tz=timezone.utc)

            payload = TokenPayload(**raw_payload)

            if expected_type and payload.type != expected_type:
                raise InvalidTokenError(
                    f"Invalid token category. Expected '{expected_type.value}', got '{payload.type.value}'."
                )

            return payload

        except jwt.ExpiredSignatureError as err:
            raise TokenExpiredError("JWT token has expired.") from err
        except (jwt.PyJWTError, ValueError) as err:
            raise InvalidTokenError(f"Failed to decode JWT token: {str(err)}") from err