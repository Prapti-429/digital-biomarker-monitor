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
from app.db.session import engine
from app.db import models  # noqa: F401 - register all ORM models
from app.middlewares.security import SecurityHeadersMiddleware
from app.middlewares.timing import ProcessTimingMiddleware

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up %s (v%s)...", settings.PROJECT_NAME, settings.VERSION)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception:
        logger.exception("Database initialization failed.")
        raise
    yield
    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://digital-biomarker-monitor.onrender.com",
]

if os.getenv("CORS_ORIGINS"):
    origins.extend([o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProcessTimingMiddleware)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root_redirect():
    return {"name": settings.PROJECT_NAME, "version": settings.VERSION, "docs": "/docs", "api_prefix": settings.API_V1_STR}


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}
