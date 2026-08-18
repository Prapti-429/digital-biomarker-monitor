"""FastAPI application entrypoint."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.base import Base
from app.db import models  # noqa: F401 - register ORM models
from app.db.session import engine
from app.middlewares.security import SecurityHeadersMiddleware
from app.middlewares.timing import ProcessTimingMiddleware

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database schema and keep the API available."""
    logger.info("Starting %s (v%s)", settings.PROJECT_NAME, settings.VERSION)
    logger.info("Database backend: %s", engine.url.get_backend_name())

    # Alembic remains available for development, but the deployed prototype
    # must be able to boot even if a migration command is unavailable. create_all
    # is idempotent and ensures registration has the required tables.
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema is ready")
    except Exception:
        logger.exception("Database initialization failed")
        raise

    yield

    logger.info("Shutting down %s", settings.PROJECT_NAME)
    engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProcessTimingMiddleware)
app.include_router(api_router, prefix=settings.API_V1_STR)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://digital-biomarker-monitor.onrender.com",
]

configured_origins = os.getenv("CORS_ORIGINS", "")
if configured_origins:
    origins.extend(
        origin.strip().rstrip("/")
        for origin in configured_origins.split(",")
        if origin.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(origins)),
    allow_origin_regex=r"https://([a-zA-Z0-9-]+\.)?onrender\.com$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "api_prefix": settings.API_V1_STR,
    }


@app.get("/health", tags=["Health"])
def health_root():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_api():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}
