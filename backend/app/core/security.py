"""Security and cryptographic utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import hashlib
import re

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import PasswordComplexityException

# Use PBKDF2 for new passwords. The previous bcrypt-only configuration can
# fail with modern bcrypt releases because Passlib 1.7.x expects a bcrypt
# backend API that is no longer exposed consistently. Keep bcrypt as a
# verification-only legacy scheme so previously-created accounts remain
# readable.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated=["bcrypt"],
)

ALGORITHM = "HS256"


def validate_password_complexity(password: str) -> str:
    reasons: list[str] = []
    if len(password) < 8:
        reasons.append("length")
    if not re.search(r"[A-Z]", password):
        reasons.append("uppercase")
    if not re.search(r"[a-z]", password):
        reasons.append("lowercase")
    if not re.search(r"\d", password):
        reasons.append("digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        reasons.append("special character")
    if reasons:
        raise PasswordComplexityException(reasons)
    return password


def _password_material(password: str) -> str:
    """Bound password input to a stable representation for all hash schemes."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """Hash a password without relying on the broken bcrypt backend path."""
    return pwd_context.hash(_password_material(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_password_material(plain_password), hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
