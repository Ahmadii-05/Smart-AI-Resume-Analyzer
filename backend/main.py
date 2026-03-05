"""
Smart AI Resume Analyzer - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

from api.routes import resume, analysis, builder, health
from core.config import settings
from core.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart AI Resume Analyzer",
    description="Production-grade AI-powered resume analysis platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(builder.router, prefix="/api/v1/builder", tags=["Builder"])


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Smart AI Resume Analyzer starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Smart AI Resume Analyzer shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
