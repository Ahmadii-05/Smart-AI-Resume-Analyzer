"""
Resume Scoring Engine
Scores resumes based on weighted criteria:
  Skills Relevance   → 30%
  Experience         → 20%
  Projects           → 15%
  Education          → 15%
  ATS Formatting     → 10%
  Keyword Relevance  → 10%
"""

import logging
import re
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

# ── Scoring weights ────────────────────────────────────────────────────────────
WEIGHTS = {
    "skills_relevance": 30,
    "experience": 20,
    "projects": 15,
    "education": 15,
    "ats_formatting": 10,
    "keyword_relevance": 10,
}

GRADE_THRESHOLDS = [
    (90, "A+", "Outstanding"),
    (80, "A",  "Excellent"),
    (70, "B+", "Good"),
    (60, "B",  "Above Average"),
    (50, "C",  "Average"),
    (40, "D",  "Below Average"),
    (0,  "F",  "Needs Significant Improvement"),
]

# High-value ATS keywords
POWER_KEYWORDS = [
    "achieved", "led", "developed", "implemented", "designed", "built",
    "reduced", "increased", "improved", "managed", "created", "launched",
    "optimized", "delivered", "collaborated", "mentored", "automated",
    "%", "million", "thousand", "$",
]


class ResumeScoringEngine:
    """
    Scores a parsed resume across 6 dimensions.
    Returns a 0-100 score with detailed breakdown and explanations.
    """

    def score(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Main scoring entry point."""
        logger.info("Scoring resume...")

        breakdown = {
            "skills_relevance": self._score_skills(parsed_resume),
            "experience": self._score_experience(parsed_resume),
            "projects": self._score_projects(parsed_resume),
            "education": self._score_education(parsed_resume),
            "ats_formatting": self._score_ats(parsed_resume),
            "keyword_relevance": self._score_keywords(parsed_resume),
        }

        total = sum(breakdown.values())
        grade, label = self._get_grade(total)
        explanation = self._generate_explanation(total, breakdown, parsed_resume)
        strengths, weaknesses = self._identify_strengths_weaknesses(breakdown)

        result = {
            "total_score": round(total, 1),
            "breakdown": breakdown,
            "grade": grade,
            "grade_label": label,
            "explanation": explanation,
            "strengths": strengths,
            "weaknesses": weaknesses,
        }

        logger.info(f"Score: {total:.1f}/100 ({grade})")
        return result

    def _score_skills(self, resume: Dict[str, Any]) -> float:
        """Score skills section (max 30 pts)."""
        skills = resume.get("skills", [])
        count = len(skills)

        if count == 0:
            return 0.0
        elif count < 5:
            base = 10.0
        elif count < 10:
            base = 18.0
        elif count < 15:
            base = 23.0
        elif count < 20:
            base = 26.0
        else:
            base = 29.0

        # Bonus for diverse skill categories
        raw_text = resume.get("raw_text", "").lower()
        from ai_engine.resume_parser.parser import TECH_SKILLS
        categories_present = sum(
            1 for cat_skills in TECH_SKILLS.values()
            if any(s in raw_text for s in cat_skills)
        )
        diversity_bonus = min(categories_present * 0.2, 1.0)

        return min(base + diversity_bonus, 30.0)

    def _score_experience(self, resume: Dict[str, Any]) -> float:
        """Score work experience section (max 20 pts)."""
        experience = resume.get("work_experience", [])
        count = len(experience)

        if count == 0:
            return 2.0  # Some credit for being entry-level
        elif count == 1:
            base = 8.0
        elif count == 2:
            base = 13.0
        elif count == 3:
            base = 16.0
        else:
            base = 18.0

        # Bonus for descriptions with bullet points
        has_descriptions = sum(
            1 for exp in experience if exp.get("description")
        )
        desc_bonus = min(has_descriptions * 0.5, 2.0)

        # Bonus for duration info
        has_duration = sum(
            1 for exp in experience if exp.get("duration")
        )
        dur_bonus = min(has_duration * 0.1, 0.5) if has_duration else 0

        return min(base + desc_bonus + dur_bonus, 20.0)

    def _score_projects(self, resume: Dict[str, Any]) -> float:
        """Score projects section (max 15 pts)."""
        projects = resume.get("projects", [])
        count = len(projects)

        if count == 0:
            return 0.0
        elif count == 1:
            base = 6.0
        elif count == 2:
            base = 10.0
        elif count == 3:
            base = 13.0
        else:
            base = 14.0

        # Bonus for projects with tech stack
        with_tech = sum(
            1 for p in projects if p.get("technologies")
        )
        tech_bonus = min(with_tech * 0.5, 1.0)

        return min(base + tech_bonus, 15.0)

    def _score_education(self, resume: Dict[str, Any]) -> float:
        """Score education section (max 15 pts)."""
        education = resume.get("education", [])

        if not education:
            return 5.0  # Some credit

        score = 10.0  # Base for having education

        for edu in education:
            degree = edu.get("degree", "").lower()
            if "phd" in degree or "doctorate" in degree:
                score = 15.0
                break
            elif "master" in degree or "m.sc" in degree or "m.tech" in degree:
                score = max(score, 14.0)
            elif "bachelor" in degree or "b.sc" in degree or "b.tech" in degree:
                score = max(score, 12.0)

        return min(score, 15.0)

    def _score_ats(self, resume: Dict[str, Any]) -> float:
        """Score ATS formatting compatibility (max 10 pts)."""
        raw_text = resume.get("raw_text", "")
        score = 0.0

        # Has email
        if resume.get("email"):
            score += 2.0

        # Has phone
        if resume.get("phone"):
            score += 1.5

        # Has skills section
        if resume.get("skills"):
            score += 2.0

        # Has experience section
        if resume.get("work_experience"):
            score += 2.0

        # Has education section
        if resume.get("education"):
            score += 1.5

        # No tables/special chars that break ATS
        special_char_count = len(re.findall(r'[│─┼┤├┬┴┘└┐┌]', raw_text))
        if special_char_count < 5:
            score += 1.0

        return min(score, 10.0)

    def _score_keywords(self, resume: Dict[str, Any]) -> float:
        """Score keyword density and impact words (max 10 pts)."""
        raw_text = resume.get("raw_text", "").lower()
        if not raw_text:
            return 0.0

        found = sum(1 for kw in POWER_KEYWORDS if kw in raw_text)
        ratio = found / len(POWER_KEYWORDS)

        return min(ratio * 10, 10.0)

    def _get_grade(self, score: float) -> Tuple[str, str]:
        for threshold, grade, label in GRADE_THRESHOLDS:
            if score >= threshold:
                return grade, label
        return "F", "Needs Significant Improvement"

    def _generate_explanation(
        self,
        total: float,
        breakdown: Dict[str, float],
        resume: Dict[str, Any],
    ) -> str:
        """Generate human-readable score explanation."""
        name = resume.get("name", "This resume")
        skill_count = len(resume.get("skills", []))
        exp_count = len(resume.get("work_experience", []))

        lines = [
            f"{name} scored {total:.0f}/100.",
            f"Found {skill_count} technical skills and {exp_count} work experience entries.",
        ]

        # Highlight top areas
        top = max(breakdown, key=breakdown.get)
        lines.append(f"Strongest area: {top.replace('_', ' ').title()} ({breakdown[top]:.1f}/{WEIGHTS[top]} pts).")

        # Highlight weak areas
        weak_areas = [
            k for k, v in breakdown.items()
            if v < WEIGHTS[k] * 0.5
        ]
        if weak_areas:
            weak_str = ", ".join(w.replace("_", " ").title() for w in weak_areas)
            lines.append(f"Areas needing improvement: {weak_str}.")

        return " ".join(lines)

    def _identify_strengths_weaknesses(
        self, breakdown: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """Classify dimensions into strengths and weaknesses."""
        strengths = []
        weaknesses = []

        labels = {
            "skills_relevance": "Technical Skills",
            "experience": "Work Experience",
            "projects": "Project Portfolio",
            "education": "Educational Background",
            "ats_formatting": "ATS-Friendly Formatting",
            "keyword_relevance": "Impact Keywords",
        }

        for dim, score in breakdown.items():
            max_score = WEIGHTS[dim]
            ratio = score / max_score
            label = labels.get(dim, dim)
            if ratio >= 0.75:
                strengths.append(f"{label} ({score:.1f}/{max_score})")
            elif ratio < 0.5:
                weaknesses.append(f"{label} ({score:.1f}/{max_score})")

        return strengths, weaknesses


# Singleton
scoring_engine = ResumeScoringEngine()
