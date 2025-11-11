"""
FitnessAI Backend - FastAPI Application Entry Point.

Main application setup with routes, middleware, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database.database import engine, Base
from src.api.v1.endpoints import health
from src.api.v1.endpoints.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events.
    
    - Startup: Create database tables (if needed)
    - Shutdown: Cleanup (if needed)
    """
    # Startup
    # Note: In production, use Alembic migrations instead of create_all
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    # Add any cleanup logic here


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="FitnessAI Backend API - AI-powered fitness training with form analysis",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

