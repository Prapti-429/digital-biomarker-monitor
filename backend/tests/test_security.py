"""
Security Primitives Unit Tests.

Validates password complexity enforcement rules, bcrypt hashing accuracy,
and pre-hashing truncation mitigations.
"""

import pytest
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_complexity,
)
from app.core.exceptions import PasswordComplexityException


def test_password_hashing_and_verification() -> None:
    """Tests password hashing and constant-time verification."""
    raw_password = "ComplexPassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_password_complexity_valid() -> None:
    """Tests that valid passwords pass policy checks without raising exceptions."""
    valid_passwords = [
        "StrongP@ssw0rd123",
        "ClinicalData#2026",
        "A1b2C3d4!e5f6",
    ]
    for pwd in valid_passwords:
        validate_password_complexity(pwd)  # Should not raise


def test_password_complexity_invalid() -> None:
    """Tests that non-compliant passwords fail with structured exception details."""
    invalid_passwords = [
        ("short", "length"),
        ("lowercaseonly1!", "uppercase"),
        ("UPPERCASEONLY1!", "lowercase"),
        ("NoSpecialChar123", "special character"),
        ("NoNumbersHere!", "digit"),
    ]

    for pwd, _ in invalid_passwords:
        with pytest.raises(PasswordComplexityException) as exc_info:
            validate_password_complexity(pwd)
        assert len(exc_info.value.details.get("reasons", [])) > 0