"""Application configuration using Pydantic Settings v2."""

from typing import Any, Optional

from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Digital Biomarker Monitor"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    JWT_SECRET_KEY: str = "dev-only-change-this-secret-before-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Render supplies DATABASE_URL for the managed PostgreSQL database.
    # Keep the individual fields as a local-development fallback.
    DATABASE_URL: Optional[str] = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "digital_biomarker_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, value: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(value, str) and value:
            return value

        database_url = info.data.get("DATABASE_URL")
        if database_url:
            # Render may provide postgres://; SQLAlchemy/psycopg2 expects
            # postgresql:// (or postgresql+psycopg2://).
            normalized = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
            if normalized.startswith("postgresql://"):
                normalized = normalized.replace("postgresql://", "postgresql+psycopg2://", 1)
            return normalized

        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )


settings = Settings()
