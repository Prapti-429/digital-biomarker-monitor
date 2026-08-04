"""
Pytest Configuration & Fixtures.

Provides reusable testing fixtures for database session handling, configuration overrides,
and temporary test database management.
"""

from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base


@pytest.fixture(scope="session")
def test_engine():
    """
    Provides a SQLAlchemy engine configured for testing.
    """
    engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        echo=False,
        pool_pre_ping=True,
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Provides a clean, transaction-isolated database session for individual test functions.
    
    Rolls back any changes at the conclusion of each test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    
    TestSessionLocal = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=Session,
    )
    
    session = TestSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()