"""
Resume Parser Module
Extracts structured data from PDF and DOCX files using NLP.
Handles: Name, Email, Phone, Skills, Education, Experience, Projects, Certifications
"""

import re
import logging
import io
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Skill Database ─────────────────────────────────────────────────────────────
TECH_SKILLS = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    ],
    "web": [
        "react", "vue", "angular", "nextjs", "nodejs", "express", "django",
        "fastapi", "flask", "spring", "laravel", "rails", "html", "css",
        "tailwind", "bootstrap", "graphql", "rest api", "webpack",
    ],
    "data": [
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "spark", "hadoop", "sql", "postgresql", "mysql", "mongodb", "redis",
        "elasticsearch", "tableau", "power bi", "excel", "matplotlib", "seaborn",
    ],
    "cloud": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
        "github actions", "ci/cd", "linux", "bash", "devops",
    ],
    "ai_ml": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "llm", "langchain", "openai", "hugging face", "transformers",
        "bert", "gpt", "neural network", "reinforcement learning",
    ],
    "soft": [
        "agile", "scrum", "jira", "git", "github", "gitlab", "communication",
        "leadership", "problem solving", "teamwork",
    ],
}

ALL_SKILLS = [skill for category in TECH_SKILLS.values() for skill in category]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "b.sc", "m.sc", "b.tech", "m.tech",
    "mba", "b.e", "m.e", "degree", "university", "college", "institute",
    "school", "diploma",
]

SECTION_HEADERS = {
    "experience": ["experience", "work experience", "employment", "work history", "professional experience"],
    "education": ["education", "academic", "qualification", "degree"],
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "projects": ["projects", "personal projects", "key projects", "portfolio"],
    "certifications": ["certifications", "certificates", "credentials", "licenses"],
    "summary": ["summary", "objective", "profile", "about"],
}


class ResumeParser:
    """
    Core resume parsing engine.
    Extracts structured information from resume text using regex + keyword matching.
    """

    def __init__(self):
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.phone_pattern = re.compile(
            r'(\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}'
        )
        self.url_pattern = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
        )
        logger.info("ResumeParser initialized")

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract raw text from PDF bytes."""
        try:
            import pdfminer.high_level
            return pdfminer.high_level.extract_text(io.BytesIO(file_bytes))
        except ImportError:
            # Fallback to PyPDF2
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            except Exception as e:
                logger.error(f"PDF extraction failed: {e}")
                return ""

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        """Extract raw text from DOCX bytes."""
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs)
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""

    def extract_name(self, text: str) -> str:
        """
        Extract candidate name from resume header.
        Strategy: First non-empty line that looks like a name.
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:5]:
            # Skip lines with email/phone/url
            if '@' in line or re.search(r'\d{5,}', line):
                continue
            # Name: 2-4 words, no special chars except hyphens
            words = line.split()
            if 2 <= len(words) <= 5 and all(
                re.match(r"^[A-Za-z\-'\.]+$", w) for w in words
            ):
                return line.title()
        return ""

    def extract_email(self, text: str) -> str:
        """Extract email address."""
        match = self.email_pattern.search(text)
        return match.group(0) if match else ""

    def extract_phone(self, text: str) -> str:
        """Extract phone number."""
        match = self.phone_pattern.search(text)
        return match.group(0).strip() if match else ""

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills using keyword matching against skill database.
        Case-insensitive matching with deduplication.
        """
        text_lower = text.lower()
        found_skills = []

        for skill in ALL_SKILLS:
            # Match whole words/phrases
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title())

        # Deduplicate preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)

        return unique_skills

    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education entries from resume text."""
        education_list = []
        lines = text.split('\n')

        in_education_section = False
        current_edu = {}

        for line in lines:
            line_lower = line.lower().strip()

            # Detect section start
            if any(kw in line_lower for kw in SECTION_HEADERS["education"]):
                in_education_section = True
                continue

            # Detect section end (another section started)
            if in_education_section and any(
                any(kw in line_lower for kw in headers)
                for section, headers in SECTION_HEADERS.items()
                if section != "education"
            ):
                if current_edu:
                    education_list.append(current_edu)
                    current_edu = {}
                in_education_section = False
                continue

            if in_education_section and line.strip():
                # Check for degree keywords
                if any(kw in line_lower for kw in EDUCATION_KEYWORDS):
                    if current_edu:
                        education_list.append(current_edu)
                    current_edu = {
                        "institution": "",
                        "degree": line.strip(),
                        "field": "",
                        "year": "",
                    }
                    # Try to extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    if year_match:
                        current_edu["year"] = year_match.group(0)
                elif current_edu and not current_edu.get("institution"):
                    current_edu["institution"] = line.strip()

        if current_edu:
            education_list.append(current_edu)

        # If nothing found via section detection, try inline detection
        if not education_list:
            for line in lines:
                line_lower = line.lower()
                if any(kw in line_lower for kw in EDUCATION_KEYWORDS) and len(line) > 10:
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    education_list.append({
                        "institution": "",
                        "degree": line.strip()[:100],
                        "field": "",
                        "year": year_match.group(0) if year_match else "",
                    })

        return education_list[:5]  # Cap at 5 entries

    def extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience entries."""
        experiences = []
        lines = text.split('\n')

        in_exp_section = False
        current_exp = None
        date_pattern = re.compile(
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|'
            r'march|april|june|july|august|september|october|november|december|\d{4})',
            re.IGNORECASE
        )

        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()

            if not line_stripped:
                continue

            if any(kw in line_lower for kw in SECTION_HEADERS["experience"]):
                in_exp_section = True
                continue

            if in_exp_section and any(
                any(kw in line_lower for kw in headers)
                for section, headers in SECTION_HEADERS.items()
                if section not in ("experience",)
            ) and len(line_stripped) < 40:
                if current_exp:
                    experiences.append(current_exp)
                    current_exp = None
                in_exp_section = False
                continue

            if in_exp_section:
                has_date = date_pattern.search(line_stripped)

                if has_date and len(line_stripped) < 80:
                    if current_exp:
                        experiences.append(current_exp)
                    current_exp = {
                        "company": "",
                        "title": line_stripped,
                        "duration": "",
                        "description": [],
                    }
                    # Extract duration
                    dur_match = re.search(
                        r'(\d{4}\s*[-–]\s*(\d{4}|present|current))', line_stripped, re.I
                    )
                    if dur_match:
                        current_exp["duration"] = dur_match.group(0)
                elif current_exp:
                    if not current_exp["company"] and len(line_stripped) < 60:
                        current_exp["company"] = line_stripped
                    elif line_stripped.startswith(('•', '-', '*', '·')):
                        current_exp["description"].append(line_stripped.lstrip('•-*· '))

        if current_exp:
            experiences.append(current_exp)

        return experiences[:10]

    def extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project entries."""
        projects = []
        lines = text.split('\n')
        in_projects = False
        current_project = None

        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()

            if any(kw in lower for kw in SECTION_HEADERS["projects"]):
                in_projects = True
                continue

            if in_projects and any(
                any(kw in lower for kw in headers)
                for section, headers in SECTION_HEADERS.items()
                if section != "projects"
            ) and len(stripped) < 40:
                if current_project:
                    projects.append(current_project)
                    current_project = None
                in_projects = False
                continue

            if in_projects and stripped:
                if not stripped.startswith(('•', '-', '*')) and len(stripped) < 80:
                    if current_project:
                        projects.append(current_project)
                    current_project = {"name": stripped, "description": "", "technologies": []}
                elif current_project:
                    desc = stripped.lstrip('•-* ')
                    current_project["description"] += desc + " "
                    # Extract tech mentioned
                    for skill in ALL_SKILLS:
                        if skill.lower() in desc.lower():
                            current_project["technologies"].append(skill.title())

        if current_project:
            projects.append(current_project)

        return projects[:8]

    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications."""
        certs = []
        lines = text.split('\n')
        in_cert_section = False

        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()

            if any(kw in lower for kw in SECTION_HEADERS["certifications"]):
                in_cert_section = True
                continue

            if in_cert_section and any(
                any(kw in lower for kw in headers)
                for section, headers in SECTION_HEADERS.items()
                if section != "certifications"
            ) and len(stripped) < 40:
                in_cert_section = False
                continue

            if in_cert_section and stripped and len(stripped) > 5:
                cert = stripped.lstrip('•-* ')
                if cert:
                    certs.append(cert)

        return certs[:10]

    def parse(self, file_bytes: bytes, file_extension: str) -> Dict[str, Any]:
        """
        Main parsing entry point.
        Returns fully structured resume data.
        """
        logger.info(f"Parsing resume: .{file_extension}")

        # Extract raw text
        if file_extension.lower() == "pdf":
            raw_text = self.extract_text_from_pdf(file_bytes)
        elif file_extension.lower() in ("docx", "doc"):
            raw_text = self.extract_text_from_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        if not raw_text or len(raw_text.strip()) < 50:
            logger.warning("Extracted text is too short; resume may be image-based")

        # Extract all fields
        result = {
            "name": self.extract_name(raw_text),
            "email": self.extract_email(raw_text),
            "phone": self.extract_phone(raw_text),
            "location": self._extract_location(raw_text),
            "skills": self.extract_skills(raw_text),
            "education": self.extract_education(raw_text),
            "work_experience": self.extract_work_experience(raw_text),
            "projects": self.extract_projects(raw_text),
            "certifications": self.extract_certifications(raw_text),
            "raw_text": raw_text,
        }

        logger.info(
            f"Parsed: name={result['name']}, "
            f"skills={len(result['skills'])}, "
            f"experience={len(result['work_experience'])}"
        )
        return result

    def _extract_location(self, text: str) -> str:
        """Extract location from header area."""
        # Look for city, state patterns
        loc_pattern = re.compile(
            r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b'
        )
        match = loc_pattern.search(text[:500])  # Check only header area
        return match.group(0) if match else ""


# Singleton instance
resume_parser = ResumeParser()
