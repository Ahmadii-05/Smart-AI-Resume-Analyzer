"""
Resume Builder Module
Generates ATS-friendly PDF resumes from structured data.
Supports multiple templates: Modern, Professional, Minimal, ATS-Friendly
"""

import logging
import os
import re
from typing import Dict, Any, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

TEMPLATE_STYLES = {
    "modern": {
        "primary_color": "#2563EB",
        "accent_color": "#DBEAFE",
        "font": "Helvetica",
        "header_style": "colored_bar",
    },
    "professional": {
        "primary_color": "#1F2937",
        "accent_color": "#F3F4F6",
        "font": "Times-Roman",
        "header_style": "classic",
    },
    "minimal": {
        "primary_color": "#374151",
        "accent_color": "#F9FAFB",
        "font": "Helvetica",
        "header_style": "minimal",
    },
    "ats_friendly": {
        "primary_color": "#000000",
        "accent_color": "#F5F5F5",
        "font": "Helvetica",
        "header_style": "simple",
    },
}


class ResumeBuilder:
    """
    Builds PDF resumes from structured data using ReportLab.
    Falls back to HTML generation if ReportLab unavailable.
    """

    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info("ResumeBuilder initialized")

    def build_pdf(self, data: Dict[str, Any], template: str = "ats_friendly") -> Dict[str, str]:
        """
        Generate PDF resume from structured data.
        Returns: {"pdf_path": str, "preview_html": str, "filename": str}
        """
        try:
            return self._build_with_reportlab(data, template)
        except ImportError:
            logger.warning("ReportLab not installed, falling back to HTML")
            return self._build_html_fallback(data, template)

    def _build_with_reportlab(self, data: Dict[str, Any], template: str) -> Dict[str, str]:
        """Generate PDF using ReportLab."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        )

        style_config = TEMPLATE_STYLES.get(template, TEMPLATE_STYLES["ats_friendly"])
        filename = f"resume_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(self.output_dir, filename)

        primary_hex = style_config["primary_color"].lstrip("#")
        primary_rgb = tuple(int(primary_hex[i:i+2], 16) / 255 for i in (0, 2, 4))
        primary_color = colors.Color(*primary_rgb)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm,
        )

        styles = getSampleStyleSheet()
        story = []

        # ── Name & Contact Header ──────────────────────────────────────────────
        name_style = ParagraphStyle(
            "name",
            parent=styles["Heading1"],
            fontSize=20,
            textColor=primary_color,
            spaceAfter=2,
            fontName=style_config["font"] + "-Bold",
        )
        contact_style = ParagraphStyle(
            "contact",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=8,
        )
        section_style = ParagraphStyle(
            "section",
            parent=styles["Heading2"],
            fontSize=11,
            textColor=primary_color,
            fontName=style_config["font"] + "-Bold",
            spaceBefore=10,
            spaceAfter=4,
            borderPadding=(0, 0, 2, 0),
        )
        body_style = ParagraphStyle(
            "body",
            parent=styles["Normal"],
            fontSize=9,
            spaceAfter=3,
            fontName=style_config["font"],
        )
        bullet_style = ParagraphStyle(
            "bullet",
            parent=styles["Normal"],
            fontSize=9,
            leftIndent=12,
            spaceAfter=2,
            bulletIndent=4,
            fontName=style_config["font"],
        )

        # Name
        story.append(Paragraph(data.get("name", "Your Name"), name_style))

        # Contact line
        contact_parts = []
        for field in ["email", "phone", "location"]:
            if data.get(field):
                contact_parts.append(data[field])
        story.append(Paragraph(" | ".join(contact_parts), contact_style))
        story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=6))

        # ── Summary ────────────────────────────────────────────────────────────
        if data.get("summary"):
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
            story.append(Paragraph(data["summary"], body_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=4))

        # ── Skills ─────────────────────────────────────────────────────────────
        skills = data.get("skills", [])
        if skills:
            story.append(Paragraph("TECHNICAL SKILLS", section_style))
            skills_text = " • ".join(skills)
            story.append(Paragraph(skills_text, body_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=4))

        # ── Work Experience ────────────────────────────────────────────────────
        experience = data.get("work_experience", [])
        if experience:
            story.append(Paragraph("WORK EXPERIENCE", section_style))
            for exp in experience:
                title_company = f"<b>{exp.get('title', '')}</b>"
                if exp.get("company"):
                    title_company += f" — {exp['company']}"
                if exp.get("duration"):
                    title_company += f" <font color='grey'>[{exp['duration']}]</font>"
                story.append(Paragraph(title_company, body_style))
                for desc in exp.get("description", [])[:5]:
                    story.append(Paragraph(f"• {desc}", bullet_style))
                story.append(Spacer(1, 3))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=4))

        # ── Education ─────────────────────────────────────────────────────────
        education = data.get("education", [])
        if education:
            story.append(Paragraph("EDUCATION", section_style))
            for edu in education:
                edu_text = f"<b>{edu.get('degree', '')}</b>"
                if edu.get("institution"):
                    edu_text += f" — {edu['institution']}"
                if edu.get("year"):
                    edu_text += f" <font color='grey'>({edu['year']})</font>"
                story.append(Paragraph(edu_text, body_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=4))

        # ── Projects ──────────────────────────────────────────────────────────
        projects = data.get("projects", [])
        if projects:
            story.append(Paragraph("PROJECTS", section_style))
            for proj in projects:
                proj_text = f"<b>{proj.get('name', '')}</b>"
                if proj.get("technologies"):
                    techs = proj["technologies"] if isinstance(proj["technologies"], list) else [proj["technologies"]]
                    proj_text += f" <font color='grey'>({', '.join(techs[:4])})</font>"
                story.append(Paragraph(proj_text, body_style))
                if proj.get("description"):
                    story.append(Paragraph(f"• {proj['description'][:200]}", bullet_style))
                story.append(Spacer(1, 2))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=4))

        # ── Certifications ────────────────────────────────────────────────────
        certs = data.get("certifications", [])
        if certs:
            story.append(Paragraph("CERTIFICATIONS", section_style))
            for cert in certs:
                story.append(Paragraph(f"• {cert}", bullet_style))

        # Build PDF
        doc.build(story)
        logger.info(f"PDF generated: {pdf_path}")

        preview_html = self._generate_preview_html(data, template)
        return {
            "pdf_path": pdf_path,
            "preview_html": preview_html,
            "filename": filename,
        }

    def _build_html_fallback(self, data: Dict[str, Any], template: str) -> Dict[str, str]:
        """Generate HTML resume as fallback."""
        style_config = TEMPLATE_STYLES.get(template, TEMPLATE_STYLES["ats_friendly"])
        filename = f"resume_{uuid.uuid4().hex[:8]}.html"
        html_path = os.path.join(self.output_dir, filename)

        html = self._generate_preview_html(data, template)
        with open(html_path, "w") as f:
            f.write(html)

        return {
            "pdf_path": html_path,
            "preview_html": html,
            "filename": filename,
        }

    def _generate_preview_html(self, data: Dict[str, Any], template: str) -> str:
        """Generate HTML preview of the resume."""
        style_config = TEMPLATE_STYLES.get(template, TEMPLATE_STYLES["ats_friendly"])
        primary = style_config["primary_color"]

        skills_html = ""
        for skill in data.get("skills", []):
            skills_html += f'<span class="skill-tag">{skill}</span>'

        exp_html = ""
        for exp in data.get("work_experience", []):
            bullets = "".join(
                f"<li>{d}</li>" for d in exp.get("description", [])[:4]
            )
            exp_html += f"""
            <div class="entry">
                <div class="entry-header">
                    <strong>{exp.get('title', '')}</strong> — {exp.get('company', '')}
                    <span class="date">{exp.get('duration', '')}</span>
                </div>
                <ul>{bullets}</ul>
            </div>"""

        edu_html = ""
        for edu in data.get("education", []):
            edu_html += f"""
            <div class="entry">
                <strong>{edu.get('degree', '')}</strong> — {edu.get('institution', '')}
                <span class="date">{edu.get('year', '')}</span>
            </div>"""

        proj_html = ""
        for proj in data.get("projects", []):
            techs = proj.get("technologies", [])
            tech_str = ", ".join(techs[:4]) if isinstance(techs, list) else str(techs)
            proj_html += f"""
            <div class="entry">
                <strong>{proj.get('name', '')}</strong>
                {f'<span class="date">{tech_str}</span>' if tech_str else ''}
                <p>{proj.get('description', '')[:150]}</p>
            </div>"""

        cert_html = "".join(
            f"<li>{c}</li>" for c in data.get("certifications", [])
        )

        contact_parts = filter(None, [data.get("email"), data.get("phone"), data.get("location")])

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; font-size: 13px; color: #333; }}
  h1 {{ color: {primary}; margin-bottom: 4px; font-size: 22px; }}
  .contact {{ color: #666; font-size: 11px; margin-bottom: 16px; }}
  h2 {{ color: {primary}; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid {primary}; padding-bottom: 4px; margin-top: 16px; }}
  .entry {{ margin-bottom: 10px; }}
  .entry-header {{ display: flex; justify-content: space-between; flex-wrap: wrap; }}
  .date {{ color: #888; font-size: 11px; }}
  ul {{ margin: 4px 0 0 0; padding-left: 16px; }}
  li {{ margin-bottom: 2px; }}
  .skill-tag {{ display: inline-block; background: {style_config['accent_color']}; color: {primary}; padding: 2px 8px; border-radius: 3px; margin: 2px; font-size: 11px; }}
  p {{ margin: 4px 0; color: #555; }}
</style>
</head>
<body>
  <h1>{data.get('name', 'Your Name')}</h1>
  <div class="contact">{' | '.join(contact_parts)}</div>
  {'<p>' + data.get('summary', '') + '</p>' if data.get('summary') else ''}
  {'<h2>Skills</h2><div>' + skills_html + '</div>' if data.get('skills') else ''}
  {'<h2>Work Experience</h2>' + exp_html if exp_html else ''}
  {'<h2>Education</h2>' + edu_html if edu_html else ''}
  {'<h2>Projects</h2>' + proj_html if proj_html else ''}
  {'<h2>Certifications</h2><ul>' + cert_html + '</ul>' if cert_html else ''}
</body>
</html>"""


# Singleton
resume_builder = ResumeBuilder()
