"""
Recommendation Engine
Generates:
  - Skill gap analysis
  - Improvement suggestions for resume content
  - Learning resource recommendations
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Curated learning paths per skill
LEARNING_RESOURCES = {
    "Python": {
        "platform": "Coursera",
        "course": "Python for Everybody",
        "url": "https://www.coursera.org/specializations/python",
        "duration": "3 months",
        "level": "Beginner",
    },
    "Machine Learning": {
        "platform": "Coursera",
        "course": "Machine Learning Specialization",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "duration": "3 months",
        "level": "Intermediate",
    },
    "Tensorflow": {
        "platform": "TensorFlow",
        "course": "TensorFlow Developer Certificate",
        "url": "https://www.tensorflow.org/certificate",
        "duration": "4 months",
        "level": "Intermediate",
    },
    "Pytorch": {
        "platform": "fast.ai",
        "course": "Practical Deep Learning",
        "url": "https://course.fast.ai",
        "duration": "2 months",
        "level": "Intermediate",
    },
    "React": {
        "platform": "Scrimba",
        "course": "Learn React",
        "url": "https://scrimba.com/learn/learnreact",
        "duration": "2 months",
        "level": "Intermediate",
    },
    "Docker": {
        "platform": "Docker",
        "course": "Docker Official Tutorial",
        "url": "https://docs.docker.com/get-started/",
        "duration": "2 weeks",
        "level": "Beginner",
    },
    "Aws": {
        "platform": "AWS",
        "course": "AWS Cloud Practitioner",
        "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
        "duration": "1 month",
        "level": "Beginner",
    },
    "Kubernetes": {
        "platform": "Linux Foundation",
        "course": "Kubernetes for Developers",
        "url": "https://training.linuxfoundation.org/training/kubernetes-for-developers/",
        "duration": "2 months",
        "level": "Advanced",
    },
    "Sql": {
        "platform": "Mode Analytics",
        "course": "SQL Tutorial",
        "url": "https://mode.com/sql-tutorial/",
        "duration": "2 weeks",
        "level": "Beginner",
    },
    "Deep Learning": {
        "platform": "deeplearning.ai",
        "course": "Deep Learning Specialization",
        "url": "https://www.deeplearning.ai/courses/deep-learning-specialization/",
        "duration": "4 months",
        "level": "Intermediate",
    },
    "Nlp": {
        "platform": "Hugging Face",
        "course": "NLP Course",
        "url": "https://huggingface.co/learn/nlp-course/",
        "duration": "2 months",
        "level": "Intermediate",
    },
    "Power Bi": {
        "platform": "Microsoft",
        "course": "Power BI Guided Learning",
        "url": "https://docs.microsoft.com/en-us/power-bi/guided-learning/",
        "duration": "1 month",
        "level": "Beginner",
    },
    "Nodejs": {
        "platform": "The Odin Project",
        "course": "NodeJS Path",
        "url": "https://www.theodinproject.com/paths/full-stack-javascript",
        "duration": "3 months",
        "level": "Intermediate",
    },
}

# Improvement templates by category
IMPROVEMENT_TEMPLATES = {
    "weak_bullets": {
        "category": "Bullet Points",
        "priority": "high",
        "suggestion": (
            "Rewrite bullet points using the STAR format (Situation, Task, Action, Result). "
            "Add quantifiable metrics: percentages, dollar amounts, time savings, team sizes."
        ),
        "example": (
            "Before: 'Worked on backend APIs'\n"
            "After: 'Designed and deployed 15 RESTful APIs using FastAPI, reducing response time by 40%'"
        ),
    },
    "no_metrics": {
        "category": "Achievements",
        "priority": "high",
        "suggestion": (
            "Add measurable achievements to every work experience entry. "
            "Quantify your impact with numbers, percentages, and timeframes."
        ),
        "example": "Include: reduced costs by 30%, managed team of 5, shipped 3 features per sprint",
    },
    "missing_summary": {
        "category": "Professional Summary",
        "priority": "medium",
        "suggestion": (
            "Add a 3-4 sentence professional summary at the top of your resume "
            "that highlights your expertise, years of experience, and key value proposition."
        ),
        "example": "Senior Python Developer with 5+ years building scalable microservices...",
    },
    "skills_section": {
        "category": "Skills",
        "priority": "high",
        "suggestion": (
            "Organize skills into categories: Programming Languages, Frameworks, "
            "Databases, Cloud & DevOps, Tools. This improves ATS parsing."
        ),
        "example": "Programming: Python, Java | Frameworks: FastAPI, React | Cloud: AWS, Docker",
    },
    "project_descriptions": {
        "category": "Projects",
        "priority": "medium",
        "suggestion": (
            "For each project, include: problem solved, technologies used, your role, "
            "and measurable outcomes. Add GitHub/demo links."
        ),
        "example": "Built a recommendation engine using collaborative filtering (Python, Scikit-learn) achieving 85% accuracy on 50K user dataset",
    },
    "ats_keywords": {
        "category": "ATS Optimization",
        "priority": "high",
        "suggestion": (
            "Mirror exact keywords from the job description in your resume. "
            "ATS systems scan for exact matches before human review."
        ),
        "example": "If JD says 'REST APIs', write 'REST APIs' not 'RESTful services'",
    },
    "education_details": {
        "category": "Education",
        "priority": "low",
        "suggestion": (
            "Include GPA (if above 3.5), relevant coursework, academic projects, "
            "and honors/awards in your education section."
        ),
        "example": "B.Sc Computer Science | GPA: 3.8/4.0 | Relevant: Algorithms, ML, Distributed Systems",
    },
    "contact_info": {
        "category": "Contact Information",
        "priority": "high",
        "suggestion": (
            "Ensure your contact section includes: Full Name, Professional Email, "
            "Phone, LinkedIn URL, GitHub URL, and City/State."
        ),
        "example": "john.doe@email.com | +1 (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe",
    },
}


class RecommendationEngine:
    """
    Analyzes resume weaknesses and generates actionable improvement suggestions.
    Maps missing skills to curated learning resources.
    """

    def generate_improvements(
        self, parsed_resume: Dict[str, Any], score_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized improvement suggestions."""
        suggestions = []
        breakdown = score_result.get("breakdown", {})

        # Check contact info
        if not parsed_resume.get("email") or not parsed_resume.get("phone"):
            suggestions.append(IMPROVEMENT_TEMPLATES["contact_info"])

        # Check skills section
        if breakdown.get("skills_relevance", 0) < 20:
            suggestions.append(IMPROVEMENT_TEMPLATES["skills_section"])

        # Check experience quality
        experiences = parsed_resume.get("work_experience", [])
        if experiences:
            has_metrics = any(
                any(
                    char in desc
                    for desc in exp.get("description", [])
                    for char in ["%", "$", "million", "thousand"]
                )
                for exp in experiences
            )
            if not has_metrics:
                suggestions.append(IMPROVEMENT_TEMPLATES["no_metrics"])

            # Check for weak bullets
            weak_bullets = sum(
                1 for exp in experiences
                if not exp.get("description") or len(exp.get("description", [])) < 2
            )
            if weak_bullets > 0:
                suggestions.append(IMPROVEMENT_TEMPLATES["weak_bullets"])
        else:
            # No experience - suggest summary
            suggestions.append(IMPROVEMENT_TEMPLATES["missing_summary"])

        # Check projects
        if breakdown.get("projects", 0) < 8:
            suggestions.append(IMPROVEMENT_TEMPLATES["project_descriptions"])

        # Check ATS score
        if breakdown.get("ats_formatting", 0) < 7:
            suggestions.append(IMPROVEMENT_TEMPLATES["ats_keywords"])

        # Check education completeness
        if breakdown.get("education", 0) < 10:
            suggestions.append(IMPROVEMENT_TEMPLATES["education_details"])

        # Deduplicate
        seen = set()
        unique = []
        for s in suggestions:
            key = s["category"]
            if key not in seen:
                seen.add(key)
                unique.append(s)

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        unique.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return unique

    def get_skill_recommendations(
        self, missing_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Map missing skills to learning resources."""
        recommendations = []

        for skill in missing_skills:
            # Normalize skill name
            normalized = skill.title()
            resource = LEARNING_RESOURCES.get(normalized)

            if resource:
                recommendations.append({
                    "skill": skill,
                    "resource": resource,
                    "priority": "high",
                })
            else:
                # Generic recommendation
                recommendations.append({
                    "skill": skill,
                    "resource": {
                        "platform": "Pluralsight / Udemy",
                        "course": f"Search: '{skill} tutorial'",
                        "url": f"https://www.udemy.com/courses/search/?q={skill.replace(' ', '+')}",
                        "duration": "Varies",
                        "level": "Beginner to Intermediate",
                    },
                    "priority": "medium",
                })

        return recommendations[:10]  # Cap recommendations

    def generate_ats_analysis(
        self, parsed_resume: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze ATS compatibility."""
        raw_text = parsed_resume.get("raw_text", "")
        issues = []
        suggestions = []

        # Check section headers
        from ai_engine.resume_parser.parser import SECTION_HEADERS
        text_lower = raw_text.lower()
        missing_sections = []
        for section, keywords in SECTION_HEADERS.items():
            if not any(kw in text_lower for kw in keywords):
                missing_sections.append(section.title())

        if missing_sections:
            issues.append(f"Missing standard sections: {', '.join(missing_sections)}")
            suggestions.append(f"Add clearly labeled sections: {', '.join(missing_sections)}")

        # Check for tables/columns (ATS unfriendly)
        import re
        special_chars = len(re.findall(r'[│─┼┤├┬┴┘└┐┌]', raw_text))
        if special_chars > 3:
            issues.append("Resume may contain tables or column layouts that confuse ATS parsers")
            suggestions.append("Use a single-column layout for better ATS compatibility")

        # Check email presence
        if not parsed_resume.get("email"):
            issues.append("Email address not detected")
            suggestions.append("Add a clearly formatted email address in the header")

        # Check for images placeholder text
        if len(raw_text) < 300:
            issues.append("Resume text is too short — may contain images or non-parseable content")
            suggestions.append("Ensure all text is selectable/copyable, not embedded in images")

        # Score calculation
        keyword_score = min(len(parsed_resume.get("skills", [])) * 3, 40)
        formatting_score = 30 - (len(issues) * 5)
        section_score = 30 - (len(missing_sections) * 5)

        ats_score = max(
            round((keyword_score + max(formatting_score, 0) + max(section_score, 0)), 1),
            10
        )
        ats_score = min(ats_score, 100)

        return {
            "ats_score": ats_score,
            "keyword_score": keyword_score,
            "formatting_score": max(formatting_score, 0),
            "section_score": max(section_score, 0),
            "issues": issues,
            "suggestions": suggestions,
        }


# Singleton
recommendation_engine = RecommendationEngine()
