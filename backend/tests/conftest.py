"""
Pytest Fixtures and Test Environment Setup.

Provides isolated in-memory SQLite database engines, FastAPI TestClients,
and pre-seeded test principals for authentication and RBAC testing.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Patch Passlib's internal bcrypt bug detector before loading passlib handlers
import passlib.handlers.bcrypt
passlib.handlers.bcrypt.detect_wrap_bug = lambda identifier: False

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

@compiles(JSONB, "sqlite")
def compile_jsonb_for_sqlite(type_, compiler, **kw):
    return "JSON"

# Application Imports with Pylance resolution hints
from app.db.session import get_db
from app.db.base import Base

try:
    from app.main import app  # type: ignore[import-not-found]
except ImportError:
    from main import app  # type: ignore[import-not-found]

try:
    from app.db.models import User  # type: ignore[import-not-found]
except ImportError:
    from db.models import User  # type: ignore[import-not-found]

try:
    from app.core.security import hash_password  # type: ignore[import-not-found]
except ImportError:
    from core.security import hash_password  # type: ignore[import-not-found]

try:
    from app.schemas.auth_enums import UserRole  # type: ignore[import-not-found]
except ImportError:
    from schemas.auth_enums import UserRole  # type: ignore[import-not-found]


# In-memory SQLite engine for isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Creates a fresh database schema for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provides a FastAPI TestClient with overridden database dependencies."""
    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_patient_user(db_session: Session) -> User:
    """Pre-seeds a verified patient user into the test database."""
    user = User(
        email="patient@example.com",
        hashed_password=hash_password("SecurePassword123!"),
        full_name="Jane Patient",
        role=UserRole.PATIENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session: Session) -> User:
    """Pre-seeds an administrator user into the test database."""
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("AdminSecurePassword123!"),
        full_name="Admin User",
        role=UserRole.ADMINISTRATOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user