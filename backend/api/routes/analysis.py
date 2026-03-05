"""
Analysis API Routes
Handles: job description matching, skill gap analysis
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.routes.resume import resume_store
from ai_engine.similarity_engine.matcher import similarity_engine
from ai_engine.recommendation_engine.recommender import recommendation_engine

logger = logging.getLogger(__name__)
router = APIRouter()


class JobMatchRequest(BaseModel):
    resume_id: str
    job_description: str


class SkillGapRequest(BaseModel):
    resume_id: str
    target_role: Optional[str] = None
    job_description: Optional[str] = None


@router.post("/job-match")
async def analyze_job_match(request: JobMatchRequest):
    """
    Compare a resume against a job description.
    Returns job fit score, matched/missing skills, and recommendations.
    """
    if request.resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    if len(request.job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description too short. Please provide at least 50 characters.",
        )

    parsed_resume = resume_store[request.resume_id]["parsed"]

    try:
        result = similarity_engine.compute_fit_score(
            parsed_resume, request.job_description
        )
    except Exception as e:
        logger.error(f"Job match error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Get learning recommendations for missing skills
    missing = result.get("missing_skills", [])
    skill_recommendations = recommendation_engine.get_skill_recommendations(missing)

    return {
        "resume_id": request.resume_id,
        "job_fit_score": result["job_fit_score"],
        "tfidf_similarity": result.get("tfidf_similarity", 0),
        "skill_match_ratio": result.get("skill_match_ratio", 0),
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "partial_skills": result["partial_skills"],
        "skill_details": result["skill_details"],
        "recommendation": result["recommendation"],
        "skill_recommendations": skill_recommendations,
        "total_jd_skills": result.get("jd_skills_count", 0),
    }


@router.post("/skill-gap")
async def analyze_skill_gap(request: SkillGapRequest):
    """
    Identify skill gaps and provide learning recommendations.
    Can work with either a job description or a target role name.
    """
    if request.resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found")

    parsed_resume = resume_store[request.resume_id]["parsed"]
    resume_skills = set(s.lower() for s in parsed_resume.get("skills", []))

    # Default role skill requirements
    ROLE_SKILL_REQUIREMENTS = {
        "data scientist": [
            "Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "SQL", "Pandas", "NumPy", "Scikit-learn", "Statistics", "Tableau",
        ],
        "backend developer": [
            "Python", "Java", "NodeJs", "PostgreSQL", "Redis", "Docker",
            "REST API", "FastAPI", "Django", "AWS", "Git",
        ],
        "frontend developer": [
            "React", "TypeScript", "JavaScript", "CSS", "HTML", "NextJS",
            "Tailwind", "GraphQL", "Git", "Testing",
        ],
        "devops engineer": [
            "Docker", "Kubernetes", "AWS", "Terraform", "Jenkins",
            "Linux", "Bash", "Monitoring", "CI/CD", "Python",
        ],
        "fullstack developer": [
            "React", "NodeJs", "Python", "PostgreSQL", "Docker",
            "REST API", "TypeScript", "Git", "AWS",
        ],
    }

    required_skills = []
    if request.job_description:
        required_skills = similarity_engine.extract_jd_skills(request.job_description)
    elif request.target_role:
        role_lower = request.target_role.lower()
        required_skills = ROLE_SKILL_REQUIREMENTS.get(
            role_lower,
            ROLE_SKILL_REQUIREMENTS.get("fullstack developer", []),
        )

    if not required_skills:
        return {
            "resume_id": request.resume_id,
            "gap_analysis": [],
            "recommendations": [],
            "message": "No target role or job description provided",
        }

    # Compute gap
    missing = [s for s in required_skills if s.lower() not in resume_skills]
    present = [s for s in required_skills if s.lower() in resume_skills]
    gap_percentage = round((len(missing) / len(required_skills)) * 100, 1)

    recommendations = recommendation_engine.get_skill_recommendations(missing)

    return {
        "resume_id": request.resume_id,
        "target_role": request.target_role or "Custom JD",
        "total_required": len(required_skills),
        "skills_present": present,
        "skills_missing": missing,
        "gap_percentage": gap_percentage,
        "coverage_percentage": round(100 - gap_percentage, 1),
        "recommendations": recommendations,
    }


@router.get("/improvements/{resume_id}")
async def get_improvements(resume_id: str):
    """Get AI-generated improvement suggestions for a resume."""
    if resume_id not in resume_store:
        raise HTTPException(status_code=404, detail="Resume not found")

    return {
        "resume_id": resume_id,
        "improvements": resume_store[resume_id].get("improvements", []),
        "ats_result": resume_store[resume_id].get("ats", {}),
    }
