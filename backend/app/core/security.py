"""
Security Primitives and Password Hashing Module.

Uses passlib with Bcrypt (cost factor 12) paired with a preliminary SHA-256 digest
step to safely digest passwords up to arbitrary lengths without byte truncation.
"""

import hashlib

from passlib.context import CryptContext
from app.core.exceptions import PasswordComplexityException

# Cryptographic context configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def _pre_hash_password(password: str) -> str:
    """
    Digest password using SHA-256 before feeding into bcrypt.
    Prevents standard Bcrypt 72-byte limit truncation vulnerabilities while
    preserving high entropy.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """
    Generates a secure salted hash for a raw password string.
    
    Args:
        password: The plain-text candidate password.
        
    Returns:
        The resulting bcrypt hash string.
    """
    pre_hashed = _pre_hash_password(password)
    return pwd_context.hash(pre_hashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a candidate plain-text password against a stored bcrypt hash in constant time.
    
    Args:
        plain_password: Raw string candidate password.
        hashed_password: Stored bcrypt digest string.
        
    Returns:
        True if credentials match; False otherwise.
    """
    pre_hashed = _pre_hash_password(plain_password)
    return pwd_context.verify(pre_hashed, hashed_password)


def validate_password_complexity(password: str) -> None:
    """
    Enforces HIPAA and NIST SP 800-63B compliant password policy rules.
    
    Rules:
    - Minimum length: 12 characters
    - At least one uppercase character
    - At least one lowercase character
    - At least one numerical digit
    - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    
    Raises:
        PasswordComplexityException: If one or more criteria are not satisfied.
    """
    reasons: list[str] = []
    
    if len(password) < 12:
        reasons.append("Password must be at least 12 characters in length.")
    if not any(c.isupper() for c in password):
        reasons.append("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password):
        reasons.append("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        reasons.append("Password must contain at least one numerical digit.")
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        reasons.append(f"Password must contain at least one special character: {special_chars}")

    if reasons:
        raise PasswordComplexityException(reasons=reasons)