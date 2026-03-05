"""
Resume Builder API Routes
"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ai_engine.resume_builder.builder import resume_builder

logger = logging.getLogger(__name__)
router = APIRouter()


class WorkExperienceInput(BaseModel):
    company: str = ""
    title: str = ""
    duration: str = ""
    description: List[str] = []


class EducationInput(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    year: str = ""


class BuildResumeRequest(BaseModel):
    name: str
    email: str
    phone: str
    location: str = ""
    summary: str = ""
    skills: List[str] = []
    education: List[EducationInput] = []
    work_experience: List[WorkExperienceInput] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    template: str = "ats_friendly"


@router.post("/generate")
async def generate_resume(request: BuildResumeRequest):
    """
    Generate a PDF resume from structured input data.
    Returns PDF download URL and HTML preview.
    """
    if not request.name or not request.email:
        raise HTTPException(status_code=400, detail="Name and email are required")

    data = request.dict()

    try:
        result = resume_builder.build_pdf(data, request.template)
    except Exception as e:
        logger.error(f"Resume build error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")

    return {
        "filename": result["filename"],
        "download_url": f"/api/v1/builder/download/{result['filename']}",
        "preview_html": result["preview_html"],
        "message": "Resume generated successfully",
    }


@router.get("/download/{filename}")
async def download_resume(filename: str):
    """Download generated resume file."""
    import os
    file_path = os.path.join("./outputs", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    media_type = "application/pdf" if filename.endswith(".pdf") else "text/html"
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=filename,
    )


@router.get("/templates")
async def list_templates():
    """List available resume templates."""
    return {
        "templates": [
            {
                "id": "modern",
                "name": "Modern",
                "description": "Clean design with colored accents. Great for tech roles.",
                "preview_color": "#2563EB",
            },
            {
                "id": "professional",
                "name": "Professional",
                "description": "Classic serif font layout. Ideal for finance and consulting.",
                "preview_color": "#1F2937",
            },
            {
                "id": "minimal",
                "name": "Minimal",
                "description": "Simple and clean. Lets your content shine.",
                "preview_color": "#374151",
            },
            {
                "id": "ats_friendly",
                "name": "ATS Friendly",
                "description": "Optimized for Applicant Tracking Systems. Best for large companies.",
                "preview_color": "#000000",
            },
        ]
    }
