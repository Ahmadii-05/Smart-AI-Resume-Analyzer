"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class TemplateType(str, Enum):
    MODERN = "modern"
    PROFESSIONAL = "professional"
    MINIMAL = "minimal"
    ATS_FRIENDLY = "ats_friendly"


# ── Resume Parsing Models ──────────────────────────────────────────────────────

class WorkExperience(BaseModel):
    company: str = ""
    title: str = ""
    duration: str = ""
    description: List[str] = []


class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    year: str = ""


class ParsedResume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    skills: List[str] = []
    education: List[Education] = []
    work_experience: List[WorkExperience] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    raw_text: str = ""


# ── Scoring Models ─────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    skills_relevance: float = Field(0, ge=0, le=30, description="0-30 points")
    experience: float = Field(0, ge=0, le=20, description="0-20 points")
    projects: float = Field(0, ge=0, le=15, description="0-15 points")
    education: float = Field(0, ge=0, le=15, description="0-15 points")
    ats_formatting: float = Field(0, ge=0, le=10, description="0-10 points")
    keyword_relevance: float = Field(0, ge=0, le=10, description="0-10 points")


class ResumeScore(BaseModel):
    total_score: float
    breakdown: ScoreBreakdown
    grade: str
    explanation: str
    strengths: List[str] = []
    weaknesses: List[str] = []


# ── Job Matching Models ────────────────────────────────────────────────────────

class JobMatchRequest(BaseModel):
    resume_id: str
    job_description: str


class SkillMatchDetail(BaseModel):
    skill: str
    status: str  # matched, missing, partial


class JobMatchResult(BaseModel):
    job_fit_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    partial_skills: List[str] = []
    skill_details: List[SkillMatchDetail] = []
    recommendation: str = ""


# ── Analysis Models ────────────────────────────────────────────────────────────

class ATSResult(BaseModel):
    ats_score: float
    keyword_score: float
    formatting_score: float
    section_score: float
    issues: List[str] = []
    suggestions: List[str] = []


class ImprovementSuggestion(BaseModel):
    category: str
    priority: str  # high, medium, low
    suggestion: str
    example: Optional[str] = None


class FullAnalysisResult(BaseModel):
    resume_id: str
    parsed_resume: ParsedResume
    score: ResumeScore
    ats_result: ATSResult
    improvements: List[ImprovementSuggestion] = []
    skill_recommendations: List[Dict[str, Any]] = []


# ── Builder Models ─────────────────────────────────────────────────────────────

class ResumeBuilderRequest(BaseModel):
    name: str
    email: str
    phone: str
    location: str = ""
    summary: str = ""
    skills: List[str] = []
    education: List[Education] = []
    work_experience: List[WorkExperience] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    template: TemplateType = TemplateType.ATS_FRIENDLY


class ResumeBuilderResponse(BaseModel):
    pdf_url: str
    preview_html: str
    filename: str
