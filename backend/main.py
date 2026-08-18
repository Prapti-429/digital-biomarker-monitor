"""
FastAPI Application Entrypoint.

Initializes the core FastAPI application instance, registers middleware, includes router
endpoints, and manages infrastructure connection lifecycle hooks.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Nuvyra API")

# Add your Render frontend URL and local dev URLs
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://digital-biomarker-monitor.onrender.com",  # Replace with your actual Render frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.api.router import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
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
    
    Verifies database connection availability on startup and disposes of engine connection pools
    gracefully on shutdown.
    """
    logger.info("Starting up %s (v%s)...", settings.PROJECT_NAME, settings.VERSION)
    yield
    logger.info("Shutting down %s... Disposing database connection pool.", settings.PROJECT_NAME)
    engine.dispose()


# Create primary FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Attach core middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProcessTimingMiddleware)

# Include main API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root_redirect():
    """
    Root entrypoint providing basic service metadata.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }