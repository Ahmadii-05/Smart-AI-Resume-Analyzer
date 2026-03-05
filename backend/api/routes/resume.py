"""
Resume API Routes
Handles: file upload, parsing, retrieval
"""

import logging
import os
import uuid
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from core.config import settings
from ai_engine.resume_parser.parser import resume_parser
from ai_engine.scoring_engine.scorer import scoring_engine
from ai_engine.recommendation_engine.recommender import recommendation_engine

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store (use Redis/DB in production)
resume_store: dict = {}


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file (PDF or DOCX).
    Returns parsed data + resume_id for subsequent operations.
    """
    # Validate file type
    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Validate file size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.1f}MB. Max: {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Save file
    resume_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{resume_id}.{ext}")
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"Saved resume: {file_path} ({size_mb:.2f}MB)")

    # Parse resume
    try:
        parsed = resume_parser.parse(content, ext)
    except Exception as e:
        logger.error(f"Parse error: {e}")
        raise HTTPException(status_code=422, detail=f"Failed to parse resume: {str(e)}")

    # Score resume
    try:
        score = scoring_engine.score(parsed)
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        score = {"total_score": 0, "breakdown": {}, "grade": "N/A", "explanation": "Scoring failed"}

    # ATS analysis
    try:
        ats = recommendation_engine.generate_ats_analysis(parsed)
    except Exception as e:
        logger.error(f"ATS analysis error: {e}")
        ats = {"ats_score": 0, "issues": [], "suggestions": []}

    # Improvements
    try:
        improvements = recommendation_engine.generate_improvements(parsed, score)
    except Exception as e:
        logger.error(f"Improvements error: {e}")
        improvements = []

    # Store for later retrieval
    resume_store[resume_id] = {
        "id": resume_id,
        "filename": file.filename,
        "parsed": parsed,
        "score": score,
        "ats": ats,
        "improvements": improvements,
        "file_path": file_path,
    }

    return {
        "resume_id": resume_id,
        "filename": file.filename,
        "parsed_resume": parsed,
        "score": score,
        "ats_result": ats,
        "improvements": improvements,
        "message": "Resume uploaded and analyzed successfully",
    }


@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    """Retrieve previously parsed resume data."""
    if resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume_store[resume_id]


@router.get("/{resume_id}/score")
async def get_resume_score(resume_id: str):
    """Get scoring details for a resume."""
    if resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume_store[resume_id]["score"]


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str):
    """Delete a resume and its data."""
    if resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found")

    entry = resume_store.pop(resume_id)
    # Remove file
    if os.path.exists(entry.get("file_path", "")):
        os.remove(entry["file_path"])

    return {"message": "Resume deleted successfully"}
