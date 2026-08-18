"""
FastAPI Application Entrypoint.

Initializes the core FastAPI application instance, registers middleware, includes router
endpoints, and manages infrastructure connection lifecycle hooks.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.base import Base  # noqa: F401 - Ensures all SQLAlchemy models are registered
from app.db.session import engine
from app.middlewares.security import SecurityHeadersMiddleware
from app.middlewares.timing import ProcessTimingMiddleware

# Initialize application logging configuration
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    Creates database tables automatically if not already present.
    """
    logger.info("Starting up %s (v%s)...", settings.PROJECT_NAME, settings.VERSION)
    try:
        # Create database tables automatically
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized/verified successfully.")
    except Exception as exc:
        logger.exception("Error initializing database tables: %s", exc)
        raise exc

    yield

    logger.info("Shutting down %s... Disposing database connection pool.", settings.PROJECT_NAME)
    engine.dispose()


# Create primary FastAPI application instance
# Docs will be accessible at both /docs and /api/v1/docs
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Allowed origins list
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://digital-biomarker-monitor.onrender.com",
]

# Merge dynamic origins from environment variables if present
env_origins = os.getenv("CORS_ORIGINS")
if env_origins:
    origins.extend([o.strip() for o in env_origins.split(",") if o.strip()])

# Attach CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Attach Security & Timing middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProcessTimingMiddleware)

# Include main API router under configured prefix (e.g. /api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root_redirect():
    """
    Root entrypoint providing service metadata and documentation links.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_V1_STR,
    }


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for Render monitoring and frontend health context.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }