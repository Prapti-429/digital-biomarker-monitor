"""Application configuration."""

import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
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

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Return Render DATABASE_URL when available, otherwise a local SQLite DB.

        SQLite is deliberately used only as a safe fallback for deployments where
        the environment variable was not injected. This keeps the prototype
        bootable instead of crashing on localhost:5432.
        """
        database_url = os.environ.get("DATABASE_URL") or self.DATABASE_URL
        if database_url:
            url = database_url.strip()
            if url.startswith("postgres://"):
                url = "postgresql://" + url[len("postgres://"):]
            return url

        return "sqlite:///./digital_biomarker.db"


settings = Settings()
