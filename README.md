# Smart AI Resume Analyzer

A production-grade, full-stack AI-powered resume analysis platform built with FastAPI + React.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│  Upload → Analysis → Job Match → Skill Gap → Builder        │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (JSON)
┌─────────────────────────▼───────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│  /api/v1/resume  /api/v1/analysis  /api/v1/builder          │
└────┬──────────────┬──────────────────────┬──────────────────┘
     │              │                      │
┌────▼────┐  ┌──────▼──────┐  ┌───────────▼──────────┐
│ Resume  │  │ Similarity  │  │  Recommendation      │
│ Parser  │  │ Engine      │  │  Engine              │
│ (spaCy/ │  │ (TF-IDF +   │  │  (Skill gaps +       │
│  regex) │  │  cosine sim)│  │   learning paths)    │
└────┬────┘  └──────┬──────┘  └───────────┬──────────┘
     │              │                      │
┌────▼──────────────▼──────────────────────▼──────────┐
│              Scoring Engine                          │
│    Skills(30) + Exp(20) + Projects(15) +             │
│    Education(15) + ATS(10) + Keywords(10) = 100      │
└──────────────────────────────────────────────────────┘
     │
┌────▼────────────┐
│ PostgreSQL DB   │
│ File Storage    │
└─────────────────┘
```

---

## 📁 Project Structure

```
smart-resume-analyzer/
├── backend/
│   ├── main.py                      # FastAPI entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── core/
│   │   ├── config.py               # Pydantic settings
│   │   └── logging_config.py       # Centralized logging
│   ├── models/
│   │   └── schemas.py              # Pydantic request/response models
│   └── api/
│       └── routes/
│           ├── resume.py           # Upload, parse, score
│           ├── analysis.py         # Job match, skill gap
│           ├── builder.py          # Resume generation
│           └── health.py           # Health check
│
├── ai_engine/
│   ├── resume_parser/
│   │   └── parser.py               # PDF/DOCX extraction + NLP
│   ├── scoring_engine/
│   │   └── scorer.py               # 6-dimension scoring (0-100)
│   ├── similarity_engine/
│   │   └── matcher.py              # TF-IDF + cosine similarity
│   ├── recommendation_engine/
│   │   └── recommender.py          # Skill gaps + learning paths
│   └── resume_builder/
│       └── builder.py              # ReportLab PDF generation
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Complete React SPA
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
git clone <repo>
cd smart-resume-analyzer
cp backend/.env.example backend/.env
docker-compose up --build
```

Open: http://localhost:3000

### Option 2: Manual Setup

**Backend (run all commands from inside the `backend` folder):**
```bash
cd backend
python -m venv venv

# Activate venv:
# Windows PowerShell:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
pip install spacy
python -m spacy download en_core_web_sm
copy .env.example .env        # Windows
# cp .env.example .env        # Mac/Linux

uvicorn main:app --reload --port 8000
```

> ⚠️ **Important:** Always run `uvicorn` from inside the `backend` folder.
> The `ai_engine` package lives at `backend/ai_engine/` so Python can find it.

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resume/upload` | Upload PDF/DOCX for full analysis |
| GET | `/api/v1/resume/{id}` | Get parsed resume data |
| GET | `/api/v1/resume/{id}/score` | Get score breakdown |
| POST | `/api/v1/analysis/job-match` | Compare resume vs JD |
| POST | `/api/v1/analysis/skill-gap` | Skill gap by role/JD |
| GET | `/api/v1/analysis/improvements/{id}` | Get AI suggestions |
| POST | `/api/v1/builder/generate` | Generate PDF resume |
| GET | `/api/v1/builder/download/{filename}` | Download generated PDF |
| GET | `/api/v1/builder/templates` | List templates |
| GET | `/api/v1/health` | Health check |

Interactive docs: http://localhost:8000/api/docs

---

## 📊 Scoring System

| Dimension | Weight | How it's scored |
|-----------|--------|-----------------|
| Skills Relevance | 30% | Count + diversity of skill categories |
| Work Experience | 20% | Number of roles + bullet quality |
| Projects | 15% | Count + tech stack presence |
| Education | 15% | Degree level detection |
| ATS Formatting | 10% | Email, phone, sections, no tables |
| Keyword Relevance | 10% | Power words & impact verbs |

**Grades:** A+(90+), A(80+), B+(70+), B(60+), C(50+), D(40+), F(<40)

---

## 🤖 AI Features

- **Resume Parsing**: Regex + keyword matching for structured extraction
- **TF-IDF Similarity**: Vectorizes resume + JD texts, computes cosine similarity
- **Skill Matching**: 3-level matching (exact, partial via fuzzy bigrams, missing)
- **ATS Analysis**: Section header detection, formatting checks, keyword density
- **Recommendations**: Curated learning paths from Coursera, AWS, fast.ai, etc.
- **Resume Builder**: ReportLab PDF generation with 4 professional templates

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, inline CSS |
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI/NLP | scikit-learn (TF-IDF), regex, keyword matching |
| PDF Generation | ReportLab |
| PDF Parsing | pdfminer.six, PyPDF2 |
| DOCX Parsing | python-docx |
| Database | PostgreSQL (optional) |
| Containerization | Docker, Docker Compose |
| Reverse Proxy | Nginx |

---

## 📖 Example API Usage

**Upload resume:**
```bash
curl -X POST http://localhost:8000/api/v1/resume/upload \
  -F "file=@my_resume.pdf"
```

**Job match:**
```bash
curl -X POST http://localhost:8000/api/v1/analysis/job-match \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": "abc123",
    "job_description": "We need a Python developer with FastAPI, Docker, AWS..."
  }'
```

**Generate resume:**
```bash
curl -X POST http://localhost:8000/api/v1/builder/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alex Chen",
    "email": "alex@email.com",
    "skills": ["Python", "React", "Docker"],
    "template": "ats_friendly"
  }'
```

---

## 📤 Example Output

```json
{
  "resume_id": "f8a2c1d4",
  "score": {
    "total_score": 82.0,
    "grade": "A",
    "breakdown": {
      "skills_relevance": 24.0,
      "experience": 17.0,
      "projects": 12.0,
      "education": 12.0,
      "ats_formatting": 9.0,
      "keyword_relevance": 8.0
    },
    "strengths": ["Technical Skills (24/30)", "Work Experience (17/20)"],
    "weaknesses": ["Keyword Relevance (8/10)"]
  },
  "ats_result": { "ats_score": 76.0 },
  "improvements": [
    {
      "category": "Achievements",
      "priority": "high",
      "suggestion": "Add measurable achievements...",
      "example": "reduced costs by 30%"
    }
  ]
}
```
