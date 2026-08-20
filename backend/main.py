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
    logger.info("Starting %s (v%s)", settings.PROJECT_NAME, settings.VERSION)
    logger.info("Database backend: %s", engine.url.get_backend_name())
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

configured_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

# NUVYRA authenticates with Bearer tokens stored by the frontend; it does not
# use browser cookies for authentication. Allowing cross-origin requests here
# prevents a Render-generated frontend hostname (or a renamed deployment) from
# turning a valid registration request into a browser-level "Network Error".
# The API still requires its normal authentication and validation rules.
app.add_middleware(
    CORSMiddleware,
    allow_origins=(configured_origins or ["*"]),
    allow_origin_regex=r"https://.*\.onrender\.com$",
    allow_credentials=False,
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
