"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Smart AI Resume Analyzer",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }
