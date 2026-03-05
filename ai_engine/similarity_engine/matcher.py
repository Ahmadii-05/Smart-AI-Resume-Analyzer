"""
Job Description Similarity Engine
Computes job fit score using:
  - TF-IDF vectorization + cosine similarity
  - Skill keyword matching
  - Sentence-level semantic analysis
"""

import logging
import re
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Common job description stop words
JD_STOP_WORDS = [
    "the", "and", "or", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "shall", "can",
    "a", "an", "in", "on", "at", "to", "for", "of", "with",
    "we", "you", "our", "your", "us", "them", "their", "this",
    "that", "these", "those", "candidate", "role", "position",
    "company", "team", "work", "working", "experience", "years",
    "ability", "strong", "good", "excellent", "great", "preferred",
    "required", "responsibilities", "requirements", "qualifications",
]


class SimilarityEngine:
    """
    Computes semantic and keyword-based similarity between
    a resume and a job description.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words=JD_STOP_WORDS,
            ngram_range=(1, 2),  # Unigrams + bigrams
            max_features=5000,
            min_df=1,
        )
        logger.info("SimilarityEngine initialized")

    def extract_jd_skills(self, jd_text: str) -> List[str]:
        """Extract required skills from job description."""
        from ai_engine.resume_parser.parser import ALL_SKILLS
        jd_lower = jd_text.lower()
        found = []
        for skill in ALL_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, jd_lower):
                found.append(skill.title())
        return list(dict.fromkeys(found))  # Deduplicate

    def compute_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Compute TF-IDF cosine similarity between two texts."""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(sim[0][0])
        except Exception as e:
            logger.error(f"TF-IDF similarity failed: {e}")
            return 0.0

    def compute_skill_overlap(
        self,
        resume_skills: List[str],
        jd_skills: List[str],
    ) -> Dict[str, Any]:
        """
        Compute skill-level match between resume and JD.
        Returns matched, missing, and partial matches.
        """
        resume_lower = {s.lower() for s in resume_skills}
        jd_lower = {s.lower(): s for s in jd_skills}

        matched = []
        missing = []
        partial = []

        for jd_skill_lower, jd_skill_original in jd_lower.items():
            # Exact match
            if jd_skill_lower in resume_lower:
                matched.append(jd_skill_original)
            else:
                # Partial match: check if any resume skill contains or is contained
                partial_match = False
                for r_skill in resume_lower:
                    if (
                        jd_skill_lower in r_skill
                        or r_skill in jd_skill_lower
                        or self._fuzzy_match(jd_skill_lower, r_skill)
                    ):
                        partial.append(jd_skill_original)
                        partial_match = True
                        break
                if not partial_match:
                    missing.append(jd_skill_original)

        return {
            "matched": matched,
            "missing": missing,
            "partial": partial,
        }

    def _fuzzy_match(self, s1: str, s2: str, threshold: float = 0.8) -> bool:
        """Simple character-level similarity for fuzzy matching."""
        if not s1 or not s2:
            return False
        # Jaccard similarity on character bigrams
        def bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1))
        b1, b2 = bigrams(s1), bigrams(s2)
        if not b1 or not b2:
            return False
        intersection = len(b1 & b2)
        union = len(b1 | b2)
        return (intersection / union) >= threshold

    def compute_fit_score(
        self,
        parsed_resume: Dict[str, Any],
        job_description: str,
    ) -> Dict[str, Any]:
        """
        Main method: compute job fit score.
        Combines TF-IDF similarity + skill match ratio.
        """
        logger.info("Computing job fit score...")

        resume_text = parsed_resume.get("raw_text", "")
        resume_skills = parsed_resume.get("skills", [])

        # 1. TF-IDF similarity (40% weight)
        tfidf_sim = self.compute_tfidf_similarity(resume_text, job_description)

        # 2. Skill-based matching (60% weight)
        jd_skills = self.extract_jd_skills(job_description)
        skill_overlap = self.compute_skill_overlap(resume_skills, jd_skills)

        total_jd_skills = len(jd_skills) or 1
        matched_count = len(skill_overlap["matched"])
        partial_count = len(skill_overlap["partial"])

        # Partial matches count as 0.5
        skill_score = (matched_count + partial_count * 0.5) / total_jd_skills

        # Combined score
        combined = (tfidf_sim * 0.4) + (skill_score * 0.6)
        fit_percentage = round(min(combined * 100, 100), 1)

        # Build skill detail list
        skill_details = []
        for s in skill_overlap["matched"]:
            skill_details.append({"skill": s, "status": "matched"})
        for s in skill_overlap["partial"]:
            skill_details.append({"skill": s, "status": "partial"})
        for s in skill_overlap["missing"]:
            skill_details.append({"skill": s, "status": "missing"})

        # Recommendation
        recommendation = self._generate_recommendation(fit_percentage, skill_overlap)

        result = {
            "job_fit_score": fit_percentage,
            "tfidf_similarity": round(tfidf_sim * 100, 1),
            "skill_match_ratio": round(skill_score * 100, 1),
            "matched_skills": skill_overlap["matched"],
            "missing_skills": skill_overlap["missing"],
            "partial_skills": skill_overlap["partial"],
            "jd_skills_count": len(jd_skills),
            "skill_details": skill_details,
            "recommendation": recommendation,
        }

        logger.info(f"Job fit score: {fit_percentage}%")
        return result

    def _generate_recommendation(
        self, score: float, overlap: Dict[str, List[str]]
    ) -> str:
        """Generate a recommendation based on fit score."""
        missing = overlap.get("missing", [])
        if score >= 80:
            return (
                "Excellent match! Your profile strongly aligns with this role. "
                "Focus on highlighting your most relevant experience in your cover letter."
            )
        elif score >= 60:
            top_missing = ", ".join(missing[:3]) if missing else "a few areas"
            return (
                f"Good match with room for improvement. Consider adding skills in {top_missing} "
                "to strengthen your application."
            )
        elif score >= 40:
            top_missing = ", ".join(missing[:5]) if missing else "several key areas"
            return (
                f"Moderate match. To improve your candidacy, develop skills in: {top_missing}. "
                "Tailor your resume to emphasize transferable skills."
            )
        else:
            return (
                "This role requires significant skill development. Consider building foundational "
                f"skills in: {', '.join(missing[:5]) if missing else 'the required tech stack'}. "
                "Look for more junior roles or upskilling resources first."
            )


# Singleton
similarity_engine = SimilarityEngine()
