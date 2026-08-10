"""
Security and Cryptographic Utility Module.

Provides password hashing, complexity validation, verification, and JWT token generation.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import re
from typing import Any, Optional, Dict
import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.exceptions import PasswordComplexityException

try:
    from app.core.config import settings  # type: ignore[import-not-found]
except ImportError:
    from core.config import settings  # type: ignore[import-not-found]




    def __init__(self, message: str, reasons: Optional[list[str]] = None):
        self.details = {
            "reasons": reasons or []
        }
        super().__init__(message)


# Password context configuring Bcrypt scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def validate_password_complexity(password: str) -> str:
    """
    Validates that a plain password meets clinical security policy:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """

    reasons: list[str] = []

    if len(password) < 8:
        reasons.append("length")

    if not re.search(r"[A-Z]", password):
        reasons.append("uppercase")

    if not re.search(r"[a-z]", password):
        reasons.append("lowercase")

    if not re.search(r"\d", password):
        reasons.append("digit")

    if not re.search(r"""[!@#$%^&*(),.?":{}|<>]""", password):
        reasons.append("special character")

    if reasons:
        raise PasswordComplexityException(reasons)

    return password

def _truncate_password(password: str) -> str:
    """Safely truncates password to 72 bytes to prevent Bcrypt ValueError."""
    # Pre-hash with SHA-256 hex digest (fixed 64 characters = 64 bytes)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()[:72]


def hash_password(password: str) -> str:
    """Hashes a plain text password safely using SHA-256 pre-hashing and Bcrypt."""
    safe_pwd = _truncate_password(password)
    return pwd_context.hash(safe_pwd)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored Bcrypt hash."""
    safe_pwd = _truncate_password(plain_password)
    return pwd_context.verify(safe_pwd, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)