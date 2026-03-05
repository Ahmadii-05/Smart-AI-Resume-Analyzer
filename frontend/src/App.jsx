import { useState, useCallback, useRef } from "react";

const API_BASE =import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

// ── Color palette & design tokens ─────────────────────────────────────────────
const THEME = {
  bg: "#0A0A0F",
  surface: "#111118",
  surfaceHigh: "#16161F",
  border: "#1E1E2E",
  borderHigh: "#2A2A3E",
  accent: "#6366F1",
  accentHover: "#818CF8",
  accentGlow: "rgba(99,102,241,0.15)",
  accentGlow2: "rgba(99,102,241,0.08)",
  success: "#10B981",
  warning: "#F59E0B",
  danger: "#EF4444",
  text: "#F1F5F9",
  textMuted: "#64748B",
  textDim: "#94A3B8",
};

// ── Utility helpers ────────────────────────────────────────────────────────────
const clamp = (val, min, max) => Math.max(min, Math.min(max, val));
const scoreColor = (s) =>
  s >= 80 ? THEME.success : s >= 60 ? THEME.warning : THEME.danger;
const gradeColor = (g) =>
  ["A+", "A"].includes(g) ? THEME.success :
  ["B+", "B"].includes(g) ? THEME.warning : THEME.danger;

// ── Mock API (when backend unavailable) ───────────────────────────────────────
const MOCK_ANALYSIS = {
  resume_id: "demo-001",
  filename: "sample_resume.pdf",
  parsed_resume: {
    name: "Alex Chen",
    email: "alex.chen@email.com",
    phone: "+1 (555) 234-5678",
    location: "San Francisco, CA",
    skills: ["Python", "React", "TypeScript", "Docker", "AWS", "PostgreSQL", "FastAPI", "Redis", "Git", "Linux"],
    education: [{ degree: "B.Sc Computer Science", institution: "UC Berkeley", year: "2020" }],
    work_experience: [
      {
        title: "Senior Software Engineer",
        company: "TechCorp",
        duration: "2021 - Present",
        description: ["Built microservices handling 1M+ requests/day", "Reduced API latency by 40%"],
      },
      {
        title: "Software Engineer",
        company: "StartupXYZ",
        duration: "2020 - 2021",
        description: ["Led React frontend development", "Implemented CI/CD pipelines"],
      },
    ],
    projects: [
      { name: "AI Chat Platform", description: "Real-time chat with GPT integration", technologies: ["React", "Python", "OpenAI"] },
      { name: "E-Commerce API", description: "RESTful API with 50K+ products", technologies: ["FastAPI", "PostgreSQL", "Redis"] },
    ],
    certifications: ["AWS Solutions Architect", "Google Cloud Professional"],
  },
  score: {
    total_score: 82,
    grade: "A",
    grade_label: "Excellent",
    breakdown: {
      skills_relevance: 24,
      experience: 17,
      projects: 12,
      education: 12,
      ats_formatting: 9,
      keyword_relevance: 8,
    },
    strengths: ["Technical Skills (24/30)", "Work Experience (17/20)"],
    weaknesses: ["Keyword Relevance (8/10)"],
    explanation: "Alex Chen scored 82/100. Found 10 technical skills and 2 work experience entries. Strongest area: Skills Relevance.",
  },
  ats_result: {
    ats_score: 76,
    keyword_score: 30,
    formatting_score: 25,
    section_score: 21,
    issues: ["Consider adding more quantifiable metrics"],
    suggestions: ["Add LinkedIn URL", "Include a professional summary"],
  },
  improvements: [
    { category: "Achievements", priority: "high", suggestion: "Add measurable achievements to every work experience entry.", example: "reduced costs by 30%, managed team of 5" },
    { category: "ATS Optimization", priority: "high", suggestion: "Mirror exact keywords from job descriptions in your resume.", example: "If JD says 'REST APIs', write 'REST APIs' not 'RESTful services'" },
    { category: "Professional Summary", priority: "medium", suggestion: "Add a 3-4 sentence professional summary at the top.", example: "Senior Python Developer with 5+ years building scalable microservices..." },
  ],
};

const MOCK_JOB_MATCH = {
  job_fit_score: 73,
  matched_skills: ["Python", "React", "Docker", "AWS", "PostgreSQL"],
  missing_skills: ["TensorFlow", "Kubernetes", "Machine Learning", "GraphQL"],
  partial_skills: ["TypeScript", "FastAPI"],
  skill_details: [
    { skill: "Python", status: "matched" }, { skill: "React", status: "matched" },
    { skill: "Docker", status: "matched" }, { skill: "TensorFlow", status: "missing" },
    { skill: "Kubernetes", status: "missing" }, { skill: "TypeScript", status: "partial" },
  ],
  recommendation: "Good match with room for improvement. Consider adding skills in TensorFlow, Kubernetes to strengthen your application.",
  skill_recommendations: [
    { skill: "TensorFlow", resource: { platform: "TensorFlow", course: "TF Developer Certificate", url: "https://tensorflow.org/certificate", duration: "4 months", level: "Intermediate" }, priority: "high" },
    { skill: "Kubernetes", resource: { platform: "Linux Foundation", course: "Kubernetes for Developers", url: "https://training.linuxfoundation.org", duration: "2 months", level: "Advanced" }, priority: "high" },
  ],
};

// ── Sub-Components ─────────────────────────────────────────────────────────────

function GlowCard({ children, style = {}, className = "" }) {
  return (
    <div style={{
      background: THEME.surface,
      border: `1px solid ${THEME.border}`,
      borderRadius: 16,
      padding: 24,
      position: "relative",
      overflow: "hidden",
      ...style,
    }}>
      {children}
    </div>
  );
}

function Badge({ children, color = THEME.accent, bg }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      padding: "3px 10px", borderRadius: 99,
      fontSize: 11, fontWeight: 600, letterSpacing: 0.5,
      color, background: bg || color + "22",
      border: `1px solid ${color}44`,
    }}>{children}</span>
  );
}

function CircleScore({ score, label, size = 120 }) {
  const color = scoreColor(score);
  const r = (size / 2) - 10;
  const circumference = 2 * Math.PI * r;
  const dash = (score / 100) * circumference;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
      <svg width={size} height={size}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={THEME.border} strokeWidth={8}/>
        <circle
          cx={size/2} cy={size/2} r={r} fill="none"
          stroke={color} strokeWidth={8}
          strokeDasharray={`${dash} ${circumference}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size/2} ${size/2})`}
          style={{ transition: "stroke-dasharray 1s ease" }}
        />
        <text x={size/2} y={size/2 - 4} textAnchor="middle" fill={THEME.text} fontSize={size/6} fontWeight="700" fontFamily="inherit">
          {score}
        </text>
        <text x={size/2} y={size/2 + 14} textAnchor="middle" fill={THEME.textMuted} fontSize={size/10} fontFamily="inherit">
          /100
        </text>
      </svg>
      {label && <span style={{ color: THEME.textDim, fontSize: 12 }}>{label}</span>}
    </div>
  );
}

function ScoreBar({ label, value, max, color }) {
  const pct = (value / max) * 100;
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ color: THEME.textDim, fontSize: 13 }}>{label}</span>
        <span style={{ color: THEME.text, fontSize: 13, fontWeight: 600 }}>{value}/{max}</span>
      </div>
      <div style={{ height: 6, background: THEME.border, borderRadius: 99, overflow: "hidden" }}>
        <div style={{
          height: "100%", width: `${pct}%`,
          background: `linear-gradient(90deg, ${color}, ${color}99)`,
          borderRadius: 99,
          transition: "width 1s ease",
          boxShadow: `0 0 8px ${color}66`,
        }}/>
      </div>
    </div>
  );
}

function SkillTag({ skill, status }) {
  const colors = {
    matched: { bg: THEME.success + "18", border: THEME.success + "44", text: THEME.success },
    missing: { bg: THEME.danger + "18", border: THEME.danger + "44", text: THEME.danger },
    partial: { bg: THEME.warning + "18", border: THEME.warning + "44", text: THEME.warning },
    default: { bg: THEME.accent + "18", border: THEME.accent + "44", text: THEME.accent },
  };
  const c = colors[status] || colors.default;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      padding: "4px 10px", borderRadius: 6, fontSize: 12, fontWeight: 500,
      color: c.text, background: c.bg, border: `1px solid ${c.border}`,
      margin: "3px",
    }}>
      {status === "matched" && "✓ "}{status === "missing" && "✗ "}{status === "partial" && "~ "}
      {skill}
    </span>
  );
}

function SectionTitle({ children, icon }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
      {icon && <span style={{ fontSize: 20 }}>{icon}</span>}
      <h3 style={{ color: THEME.text, fontSize: 16, fontWeight: 700, margin: 0 }}>{children}</h3>
      <div style={{ flex: 1, height: 1, background: `linear-gradient(90deg, ${THEME.border}, transparent)`, marginLeft: 8 }}/>
    </div>
  );
}

function Spinner() {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16, padding: 48 }}>
      <div style={{
        width: 48, height: 48, border: `3px solid ${THEME.border}`,
        borderTop: `3px solid ${THEME.accent}`,
        borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
      }}/>
      <span style={{ color: THEME.textDim, fontSize: 14 }}>Analyzing with AI...</span>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

// ── Upload Page ────────────────────────────────────────────────────────────────
function UploadPage({ onAnalyzed, setActiveTab }) {
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileRef = useRef();

  const handleFile = useCallback(async (file) => {
    if (!file) return;
    const ext = file.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx"].includes(ext)) {
      setError("Only PDF and DOCX files are supported.");
      return;
    }
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/resume/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
      const data = await res.json();
      onAnalyzed(data);
      setActiveTab("analysis");
    } catch (e) {
      // Use mock data for demo
      console.warn("Backend unavailable, using demo data:", e.message);
      onAnalyzed({ ...MOCK_ANALYSIS, filename: file.name });
      setActiveTab("analysis");
    } finally {
      setLoading(false);
    }
  }, [onAnalyzed, setActiveTab]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "48px 0" }}>
      {/* Hero */}
      <div style={{ textAlign: "center", marginBottom: 48 }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: 8,
          padding: "6px 16px", borderRadius: 99,
          background: THEME.accentGlow,
          border: `1px solid ${THEME.accent}44`,
          color: THEME.accent, fontSize: 13, fontWeight: 600,
          marginBottom: 24,
        }}>
          <span>✦</span> AI-Powered Resume Intelligence
        </div>
        <h1 style={{
          fontSize: 48, fontWeight: 800, margin: "0 0 16px",
          background: `linear-gradient(135deg, ${THEME.text} 0%, ${THEME.accent} 100%)`,
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          lineHeight: 1.1,
        }}>
          Analyze Your Resume<br/>with AI Precision
        </h1>
        <p style={{ color: THEME.textMuted, fontSize: 16, maxWidth: 480, margin: "0 auto" }}>
          Get instant scoring, job-fit analysis, skill gap detection,
          and ATS optimization — all in one place.
        </p>
      </div>

      {/* Upload zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => !loading && fileRef.current?.click()}
        style={{
          border: `2px dashed ${dragOver ? THEME.accent : THEME.borderHigh}`,
          borderRadius: 20,
          padding: "56px 32px",
          textAlign: "center",
          cursor: loading ? "not-allowed" : "pointer",
          background: dragOver ? THEME.accentGlow : THEME.surface,
          transition: "all 0.2s ease",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {loading ? <Spinner /> : (
          <>
            <div style={{ fontSize: 56, marginBottom: 16 }}>📄</div>
            <h3 style={{ color: THEME.text, fontSize: 20, fontWeight: 700, margin: "0 0 8px" }}>
              Drop your resume here
            </h3>
            <p style={{ color: THEME.textMuted, margin: "0 0 24px" }}>
              or click to browse files
            </p>
            <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
              <Badge>PDF</Badge>
              <Badge>DOCX</Badge>
              <Badge color={THEME.textMuted}>Max 10MB</Badge>
            </div>
          </>
        )}
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx"
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>

      {error && (
        <div style={{
          marginTop: 16, padding: "12px 16px", borderRadius: 10,
          background: THEME.danger + "18", border: `1px solid ${THEME.danger}44`,
          color: THEME.danger, fontSize: 14,
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Feature cards */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginTop: 48 }}>
        {[
          { icon: "🎯", title: "Smart Scoring", desc: "6-dimension resume scoring with detailed breakdown" },
          { icon: "🔍", title: "Job Matching", desc: "Compare against any job description with AI" },
          { icon: "📈", title: "Skill Gaps", desc: "Discover missing skills with learning paths" },
          { icon: "🤖", title: "ATS Check", desc: "Ensure your resume passes ATS filters" },
          { icon: "💡", title: "AI Suggestions", desc: "Actionable improvements prioritized for impact" },
          { icon: "🏗️", title: "Resume Builder", desc: "Generate ATS-friendly resumes from templates" },
        ].map((f) => (
          <GlowCard key={f.title} style={{ padding: 20, textAlign: "center" }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>{f.icon}</div>
            <div style={{ color: THEME.text, fontWeight: 600, fontSize: 13, marginBottom: 4 }}>{f.title}</div>
            <div style={{ color: THEME.textMuted, fontSize: 12, lineHeight: 1.5 }}>{f.desc}</div>
          </GlowCard>
        ))}
      </div>
    </div>
  );
}

// ── Analysis Page ──────────────────────────────────────────────────────────────
function AnalysisPage({ data }) {
  if (!data) return (
    <div style={{ textAlign: "center", padding: 80, color: THEME.textMuted }}>
      No resume analyzed yet. Upload a resume to get started.
    </div>
  );

  const { parsed_resume: pr, score, ats_result: ats, improvements } = data;

  const breakdownLabels = {
    skills_relevance: { label: "Skills Relevance", max: 30 },
    experience: { label: "Work Experience", max: 20 },
    projects: { label: "Projects", max: 15 },
    education: { label: "Education", max: 15 },
    ats_formatting: { label: "ATS Formatting", max: 10 },
    keyword_relevance: { label: "Keyword Relevance", max: 10 },
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto" }}>
      {/* Header row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32, flexWrap: "wrap", gap: 16 }}>
        <div>
          <h2 style={{ color: THEME.text, fontSize: 24, fontWeight: 800, margin: "0 0 4px" }}>
            Resume Analysis
          </h2>
          <span style={{ color: THEME.textMuted, fontSize: 14 }}>📄 {data.filename}</span>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <Badge color={gradeColor(score.grade)} bg={gradeColor(score.grade) + "18"}>
            Grade: {score.grade} — {score.grade_label}
          </Badge>
        </div>
      </div>

      {/* Score cards row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 20, marginBottom: 24 }}>
        <GlowCard style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, padding: 32 }}>
          <CircleScore score={score.total_score} label="Resume Score" />
          <p style={{ color: THEME.textMuted, fontSize: 12, textAlign: "center", margin: 0 }}>
            {score.explanation.split(".")[0]}.
          </p>
        </GlowCard>

        <GlowCard style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, padding: 32 }}>
          <CircleScore score={ats.ats_score} label="ATS Score" />
          <p style={{ color: THEME.textMuted, fontSize: 12, textAlign: "center", margin: 0 }}>
            ATS compatibility rating
          </p>
        </GlowCard>

        <GlowCard style={{ padding: 24 }}>
          <SectionTitle icon="👤">Candidate</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { icon: "🏷️", val: pr.name || "—" },
              { icon: "✉️", val: pr.email || "—" },
              { icon: "📱", val: pr.phone || "—" },
              { icon: "📍", val: pr.location || "—" },
            ].map(({ icon, val }) => (
              <div key={val} style={{ display: "flex", gap: 8, fontSize: 13 }}>
                <span>{icon}</span>
                <span style={{ color: THEME.textDim }}>{val}</span>
              </div>
            ))}
          </div>
        </GlowCard>
      </div>

      {/* Score breakdown + improvements */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
        <GlowCard>
          <SectionTitle icon="📊">Score Breakdown</SectionTitle>
          {Object.entries(score.breakdown).map(([key, val]) => {
            const { label, max } = breakdownLabels[key] || { label: key, max: 10 };
            const pct = (val / max) * 100;
            const color = pct >= 75 ? THEME.success : pct >= 50 ? THEME.warning : THEME.danger;
            return <ScoreBar key={key} label={label} value={val} max={max} color={color} />;
          })}
        </GlowCard>

        <GlowCard>
          <SectionTitle icon="💡">Improvements</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {(improvements || []).slice(0, 4).map((imp, i) => (
              <div key={i} style={{
                padding: 14, borderRadius: 10,
                background: THEME.surfaceHigh,
                border: `1px solid ${THEME.borderHigh}`,
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <Badge
                    color={imp.priority === "high" ? THEME.danger : imp.priority === "medium" ? THEME.warning : THEME.success}
                  >
                    {imp.priority}
                  </Badge>
                  <span style={{ color: THEME.text, fontSize: 13, fontWeight: 600 }}>{imp.category}</span>
                </div>
                <p style={{ color: THEME.textMuted, fontSize: 12, margin: 0, lineHeight: 1.6 }}>
                  {imp.suggestion}
                </p>
                {imp.example && (
                  <div style={{
                    marginTop: 8, padding: "6px 10px", borderRadius: 6,
                    background: THEME.accent + "0E",
                    border: `1px solid ${THEME.accent}22`,
                    color: THEME.accent, fontSize: 11, fontFamily: "monospace",
                  }}>
                    {imp.example}
                  </div>
                )}
              </div>
            ))}
          </div>
        </GlowCard>
      </div>

      {/* Skills + ATS issues */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
        <GlowCard>
          <SectionTitle icon="⚡">Detected Skills ({pr.skills?.length || 0})</SectionTitle>
          <div style={{ display: "flex", flexWrap: "wrap" }}>
            {(pr.skills || []).map((s) => (
              <SkillTag key={s} skill={s} />
            ))}
          </div>
        </GlowCard>

        <GlowCard>
          <SectionTitle icon="🧑‍💻">ATS Analysis</SectionTitle>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 16 }}>
            {[
              { label: "Keywords", val: ats.keyword_score, max: 40 },
              { label: "Formatting", val: ats.formatting_score, max: 30 },
              { label: "Sections", val: ats.section_score, max: 30 },
            ].map(({ label, val, max }) => (
              <div key={label} style={{
                textAlign: "center", padding: 12, borderRadius: 10,
                background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
              }}>
                <div style={{ color: THEME.text, fontWeight: 700, fontSize: 18 }}>{val}</div>
                <div style={{ color: THEME.textMuted, fontSize: 11 }}>{label}/{max}</div>
              </div>
            ))}
          </div>
          {ats.issues?.length > 0 && (
            <div>
              <div style={{ color: THEME.textDim, fontSize: 12, marginBottom: 8, fontWeight: 600 }}>ISSUES</div>
              {ats.issues.map((issue, i) => (
                <div key={i} style={{ display: "flex", gap: 8, marginBottom: 6, fontSize: 12, color: THEME.textMuted }}>
                  <span style={{ color: THEME.danger }}>⚠</span> {issue}
                </div>
              ))}
            </div>
          )}
          {ats.suggestions?.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <div style={{ color: THEME.textDim, fontSize: 12, marginBottom: 8, fontWeight: 600 }}>SUGGESTIONS</div>
              {ats.suggestions.map((s, i) => (
                <div key={i} style={{ display: "flex", gap: 8, marginBottom: 6, fontSize: 12, color: THEME.textMuted }}>
                  <span style={{ color: THEME.success }}>✓</span> {s}
                </div>
              ))}
            </div>
          )}
        </GlowCard>
      </div>

      {/* Strengths / Weaknesses */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <GlowCard>
          <SectionTitle icon="✊">Strengths</SectionTitle>
          {(score.strengths || []).map((s, i) => (
            <div key={i} style={{ display: "flex", gap: 10, padding: "8px 0", borderBottom: `1px solid ${THEME.border}`, fontSize: 13 }}>
              <span style={{ color: THEME.success, fontSize: 16 }}>✦</span>
              <span style={{ color: THEME.textDim }}>{s}</span>
            </div>
          ))}
          {(!score.strengths || score.strengths.length === 0) && (
            <p style={{ color: THEME.textMuted, fontSize: 13 }}>Upload a more detailed resume to identify strengths.</p>
          )}
        </GlowCard>
        <GlowCard>
          <SectionTitle icon="📈">Areas to Improve</SectionTitle>
          {(score.weaknesses || []).map((w, i) => (
            <div key={i} style={{ display: "flex", gap: 10, padding: "8px 0", borderBottom: `1px solid ${THEME.border}`, fontSize: 13 }}>
              <span style={{ color: THEME.warning, fontSize: 16 }}>◆</span>
              <span style={{ color: THEME.textDim }}>{w}</span>
            </div>
          ))}
          {(!score.weaknesses || score.weaknesses.length === 0) && (
            <p style={{ color: THEME.textMuted, fontSize: 13 }}>Great job! No major weak areas detected.</p>
          )}
        </GlowCard>
      </div>
    </div>
  );
}

// ── Job Match Page ─────────────────────────────────────────────────────────────
function JobMatchPage({ analysisData }) {
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!jd.trim() || jd.length < 50) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/analysis/job-match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_id: analysisData?.resume_id || "demo",
          job_description: jd,
        }),
      });
      if (!res.ok) throw new Error("Failed");
      setResult(await res.json());
    } catch {
      setResult(MOCK_JOB_MATCH);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto" }}>
      <h2 style={{ color: THEME.text, fontSize: 24, fontWeight: 800, marginBottom: 8 }}>Job Description Matching</h2>
      <p style={{ color: THEME.textMuted, fontSize: 14, marginBottom: 32 }}>
        Paste a job description to see how well your resume matches the role
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <GlowCard>
          <SectionTitle icon="📋">Job Description</SectionTitle>
          <textarea
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste the full job description here...

Example:
We are looking for a Senior Python Developer with:
- 3+ years Python experience
- FastAPI, Django or Flask
- PostgreSQL, Redis
- Docker, Kubernetes
- Machine Learning experience preferred..."
            style={{
              width: "100%", height: 280, background: THEME.surfaceHigh,
              border: `1px solid ${THEME.borderHigh}`, borderRadius: 10,
              color: THEME.text, fontSize: 13, padding: 14,
              resize: "vertical", outline: "none", fontFamily: "inherit",
              lineHeight: 1.6, boxSizing: "border-box",
            }}
          />
          <button
            onClick={analyze}
            disabled={loading || jd.length < 50}
            style={{
              marginTop: 16, width: "100%", padding: "12px 0",
              background: loading ? THEME.border : `linear-gradient(135deg, ${THEME.accent}, ${THEME.accentHover})`,
              color: loading ? THEME.textMuted : "#fff",
              border: "none", borderRadius: 10, cursor: loading ? "not-allowed" : "pointer",
              fontSize: 14, fontWeight: 700, transition: "all 0.2s",
              boxShadow: loading ? "none" : `0 4px 20px ${THEME.accent}40`,
            }}
          >
            {loading ? "Analyzing..." : "⚡ Analyze Match"}
          </button>
        </GlowCard>

        {result ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Fit score */}
            <GlowCard style={{ display: "flex", alignItems: "center", gap: 24, padding: 28 }}>
              <CircleScore score={result.job_fit_score} label="Job Fit" size={100} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, color: THEME.textMuted, marginBottom: 12 }}>
                  {result.recommendation}
                </div>
                <div style={{ display: "flex", gap: 12 }}>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ color: THEME.success, fontWeight: 700, fontSize: 20 }}>{result.matched_skills?.length}</div>
                    <div style={{ color: THEME.textMuted, fontSize: 11 }}>Matched</div>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ color: THEME.warning, fontWeight: 700, fontSize: 20 }}>{result.partial_skills?.length}</div>
                    <div style={{ color: THEME.textMuted, fontSize: 11 }}>Partial</div>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ color: THEME.danger, fontWeight: 700, fontSize: 20 }}>{result.missing_skills?.length}</div>
                    <div style={{ color: THEME.textMuted, fontSize: 11 }}>Missing</div>
                  </div>
                </div>
              </div>
            </GlowCard>

            {/* Skill details */}
            <GlowCard>
              <SectionTitle icon="🎯">Skill Match Details</SectionTitle>
              <div style={{ display: "flex", flexWrap: "wrap" }}>
                {result.skill_details?.map(({ skill, status }) => (
                  <SkillTag key={skill} skill={skill} status={status} />
                ))}
              </div>
            </GlowCard>

            {/* Learning recommendations */}
            {result.skill_recommendations?.length > 0 && (
              <GlowCard>
                <SectionTitle icon="📚">Learning Recommendations</SectionTitle>
                {result.skill_recommendations.slice(0, 3).map((rec, i) => (
                  <div key={i} style={{
                    padding: 14, borderRadius: 10, marginBottom: 10,
                    background: THEME.surfaceHigh,
                    border: `1px solid ${THEME.borderHigh}`,
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                      <span style={{ color: THEME.text, fontWeight: 600, fontSize: 13 }}>{rec.skill}</span>
                      <Badge color={THEME.accent}>{rec.resource.level}</Badge>
                    </div>
                    <div style={{ color: THEME.textDim, fontSize: 12 }}>
                      {rec.resource.platform} — {rec.resource.course}
                    </div>
                    <div style={{ color: THEME.textMuted, fontSize: 11, marginTop: 4 }}>
                      Duration: {rec.resource.duration}
                    </div>
                  </div>
                ))}
              </GlowCard>
            )}
          </div>
        ) : (
          <GlowCard style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 400 }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>🎯</div>
            <div style={{ color: THEME.textMuted, fontSize: 14, textAlign: "center" }}>
              Paste a job description and click Analyze Match<br/>to see your fit score
            </div>
          </GlowCard>
        )}
      </div>
    </div>
  );
}

// ── Skill Gap Page ─────────────────────────────────────────────────────────────
function SkillGapPage({ analysisData }) {
  const [role, setRole] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const PRESET_ROLES = [
    "Data Scientist", "Backend Developer", "Frontend Developer",
    "DevOps Engineer", "Fullstack Developer",
  ];

  const analyze = async (targetRole) => {
    const r = targetRole || role;
    if (!r) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/analysis/skill-gap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_id: analysisData?.resume_id || "demo",
          target_role: r,
        }),
      });
      if (!res.ok) throw new Error("Failed");
      setResult(await res.json());
    } catch {
      // Mock data
      setResult({
        target_role: r,
        total_required: 10,
        skills_present: ["Python", "React", "Docker", "AWS", "PostgreSQL"],
        skills_missing: ["TensorFlow", "Kubernetes", "Machine Learning", "GraphQL", "Spark"],
        gap_percentage: 50,
        coverage_percentage: 50,
        recommendations: MOCK_JOB_MATCH.skill_recommendations,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto" }}>
      <h2 style={{ color: THEME.text, fontSize: 24, fontWeight: 800, marginBottom: 8 }}>Skill Gap Analysis</h2>
      <p style={{ color: THEME.textMuted, fontSize: 14, marginBottom: 32 }}>
        Discover what skills you need for your target role
      </p>

      {/* Role selector */}
      <GlowCard style={{ marginBottom: 24 }}>
        <SectionTitle icon="🎯">Select Target Role</SectionTitle>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 16 }}>
          {PRESET_ROLES.map((r) => (
            <button
              key={r}
              onClick={() => { setRole(r); analyze(r); }}
              style={{
                padding: "8px 18px", borderRadius: 8, fontSize: 13, fontWeight: 600,
                cursor: "pointer", transition: "all 0.15s",
                background: role === r ? THEME.accent : THEME.surfaceHigh,
                color: role === r ? "#fff" : THEME.textDim,
                border: `1px solid ${role === r ? THEME.accent : THEME.borderHigh}`,
              }}
            >{r}</button>
          ))}
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="Or type a custom role..."
            style={{
              flex: 1, padding: "10px 14px", borderRadius: 8,
              background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
              color: THEME.text, fontSize: 13, outline: "none",
            }}
          />
          <button
            onClick={() => analyze()}
            disabled={!role || loading}
            style={{
              padding: "10px 24px", borderRadius: 8,
              background: `linear-gradient(135deg, ${THEME.accent}, ${THEME.accentHover})`,
              color: "#fff", border: "none", cursor: "pointer",
              fontSize: 13, fontWeight: 700,
            }}
          >
            {loading ? "..." : "Analyze"}
          </button>
        </div>
      </GlowCard>

      {result && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Coverage gauge */}
            <GlowCard style={{ textAlign: "center", padding: 32 }}>
              <CircleScore score={result.coverage_percentage} label={`${result.target_role} Coverage`} />
              <p style={{ color: THEME.textMuted, fontSize: 13, marginTop: 12 }}>
                You have {result.skills_present?.length} of {result.total_required} required skills
              </p>
            </GlowCard>

            {/* Present skills */}
            <GlowCard>
              <SectionTitle icon="✅">Skills You Have</SectionTitle>
              <div style={{ display: "flex", flexWrap: "wrap" }}>
                {result.skills_present?.map((s) => <SkillTag key={s} skill={s} status="matched" />)}
              </div>
            </GlowCard>

            {/* Missing skills */}
            <GlowCard>
              <SectionTitle icon="❌">Missing Skills</SectionTitle>
              <div style={{ display: "flex", flexWrap: "wrap" }}>
                {result.skills_missing?.map((s) => <SkillTag key={s} skill={s} status="missing" />)}
              </div>
            </GlowCard>
          </div>

          {/* Learning paths */}
          <GlowCard>
            <SectionTitle icon="🗺️">Learning Roadmap</SectionTitle>
            {result.recommendations?.slice(0, 6).map((rec, i) => (
              <div key={i} style={{
                padding: 16, borderRadius: 12, marginBottom: 12,
                background: THEME.surfaceHigh,
                border: `1px solid ${THEME.borderHigh}`,
                position: "relative", overflow: "hidden",
              }}>
                <div style={{
                  position: "absolute", left: 0, top: 0, bottom: 0, width: 3,
                  background: rec.priority === "high" ? THEME.danger : THEME.warning,
                }}/>
                <div style={{ paddingLeft: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ color: THEME.text, fontWeight: 700, fontSize: 14 }}>{rec.skill}</span>
                    <Badge color={rec.priority === "high" ? THEME.danger : THEME.warning}>
                      {rec.priority} priority
                    </Badge>
                  </div>
                  <div style={{ color: THEME.textDim, fontSize: 12, marginBottom: 4 }}>
                    📚 {rec.resource.platform} — {rec.resource.course}
                  </div>
                  <div style={{ display: "flex", gap: 12, fontSize: 11, color: THEME.textMuted }}>
                    <span>⏱ {rec.resource.duration}</span>
                    <span>📊 {rec.resource.level}</span>
                  </div>
                  <a
                    href={rec.resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: THEME.accent, fontSize: 12, textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 4, marginTop: 8 }}
                  >
                    Start Learning →
                  </a>
                </div>
              </div>
            ))}
          </GlowCard>
        </div>
      )}
    </div>
  );
}

// ── Resume Builder Page ────────────────────────────────────────────────────────
function BuilderPage() {
  const [step, setStep] = useState(0);
  const [template, setTemplate] = useState("ats_friendly");
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState(null);
  const [form, setForm] = useState({
    name: "", email: "", phone: "", location: "", summary: "",
    skills: "", certifications: "",
    education: [{ institution: "", degree: "", year: "" }],
    work_experience: [{ company: "", title: "", duration: "", description: [""] }],
    projects: [{ name: "", description: "", technologies: "" }],
  });

  const update = (field, val) => setForm((p) => ({ ...p, [field]: val }));
  const updateArr = (field, idx, key, val) => {
    const arr = [...form[field]];
    arr[idx] = { ...arr[idx], [key]: val };
    setForm((p) => ({ ...p, [field]: arr }));
  };
  const addItem = (field, template) => setForm((p) => ({ ...p, [field]: [...p[field], template] }));

  const generate = async () => {
    setLoading(true);
    const payload = {
      ...form,
      skills: form.skills.split(",").map((s) => s.trim()).filter(Boolean),
      certifications: form.certifications.split(",").map((s) => s.trim()).filter(Boolean),
      projects: form.projects.map((p) => ({
        ...p,
        technologies: p.technologies.split(",").map((t) => t.trim()).filter(Boolean),
      })),
      work_experience: form.work_experience.map((e) => ({
        ...e,
        description: e.description.filter(Boolean),
      })),
      template,
    };

    try {
      const res = await fetch(`${API_BASE}/builder/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      setGenerated(data);
    } catch {
      // Mock preview
      setGenerated({
        filename: "resume_preview.html",
        preview_html: `<div style="font-family:Arial;max-width:700px;margin:0 auto;padding:20px;font-size:13px">
          <h1 style="color:#6366F1;font-size:22px;margin:0 0 4px">${form.name || "Your Name"}</h1>
          <p style="color:#666;font-size:11px">${form.email} | ${form.phone} | ${form.location}</p>
          <hr style="border-color:#6366F1;margin:12px 0">
          <h2 style="color:#6366F1;font-size:13px;text-transform:uppercase;letter-spacing:1px">Skills</h2>
          <p>${form.skills || "Add your skills above"}</p>
          <h2 style="color:#6366F1;font-size:13px;text-transform:uppercase;letter-spacing:1px">Experience</h2>
          ${form.work_experience.map(e => `<p><b>${e.title}</b> — ${e.company} <span style="color:#888">${e.duration}</span></p>`).join("")}
        </div>`,
        download_url: "#",
      });
    } finally {
      setLoading(false);
    }
  };

  const TEMPLATES = [
    { id: "ats_friendly", name: "ATS Friendly", color: "#000", desc: "Maximum ATS compatibility" },
    { id: "modern", name: "Modern", color: "#2563EB", desc: "Clean with blue accents" },
    { id: "professional", name: "Professional", color: "#1F2937", desc: "Classic serif style" },
    { id: "minimal", name: "Minimal", color: "#374151", desc: "Simple and clean" },
  ];

  const STEPS = ["Personal", "Skills", "Experience", "Education", "Projects", "Template"];

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto" }}>
      <h2 style={{ color: THEME.text, fontSize: 24, fontWeight: 800, marginBottom: 8 }}>Resume Builder</h2>
      <p style={{ color: THEME.textMuted, fontSize: 14, marginBottom: 32 }}>
        Build an ATS-optimized resume with a professional template
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 24, alignItems: "start" }}>
        {/* Step nav */}
        <div style={{ display: "flex", flexDirection: "column", gap: 0, position: "sticky", top: 20 }}>
          {STEPS.map((s, i) => (
            <button
              key={s}
              onClick={() => setStep(i)}
              style={{
                padding: "12px 16px", textAlign: "left",
                background: step === i ? THEME.accentGlow : "transparent",
                border: "none", borderLeft: `3px solid ${step === i ? THEME.accent : THEME.border}`,
                color: step === i ? THEME.accent : THEME.textMuted,
                cursor: "pointer", fontSize: 14, fontWeight: step === i ? 700 : 400,
                transition: "all 0.15s",
                borderRadius: step === i ? "0 8px 8px 0" : "0",
              }}
            >
              <span style={{ marginRight: 10 }}>
                {["👤", "⚡", "💼", "🎓", "🚀", "🎨"][i]}
              </span>
              {s}
            </button>
          ))}
          <button
            onClick={generate}
            disabled={!form.name || !form.email || loading}
            style={{
              marginTop: 20, padding: "14px 16px", borderRadius: 10,
              background: `linear-gradient(135deg, ${THEME.accent}, ${THEME.accentHover})`,
              color: "#fff", border: "none", cursor: "pointer",
              fontSize: 14, fontWeight: 700,
              boxShadow: `0 4px 20px ${THEME.accent}40`,
            }}
          >
            {loading ? "Generating..." : "⚡ Generate Resume"}
          </button>
        </div>

        {/* Step content */}
        <div>
          {step === 0 && (
            <GlowCard>
              <SectionTitle icon="👤">Personal Information</SectionTitle>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                {[
                  { label: "Full Name *", field: "name", placeholder: "Alex Chen" },
                  { label: "Email *", field: "email", placeholder: "alex@email.com" },
                  { label: "Phone", field: "phone", placeholder: "+1 (555) 123-4567" },
                  { label: "Location", field: "location", placeholder: "San Francisco, CA" },
                ].map(({ label, field, placeholder }) => (
                  <div key={field}>
                    <label style={{ color: THEME.textDim, fontSize: 12, fontWeight: 600, display: "block", marginBottom: 6 }}>{label}</label>
                    <input
                      value={form[field]}
                      onChange={(e) => update(field, e.target.value)}
                      placeholder={placeholder}
                      style={{
                        width: "100%", padding: "10px 12px", borderRadius: 8,
                        background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
                        color: THEME.text, fontSize: 13, outline: "none", boxSizing: "border-box",
                      }}
                    />
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 14 }}>
                <label style={{ color: THEME.textDim, fontSize: 12, fontWeight: 600, display: "block", marginBottom: 6 }}>Professional Summary</label>
                <textarea
                  value={form.summary}
                  onChange={(e) => update("summary", e.target.value)}
                  placeholder="Senior Full Stack Developer with 5+ years building scalable web applications..."
                  style={{
                    width: "100%", height: 100, padding: "10px 12px", borderRadius: 8,
                    background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
                    color: THEME.text, fontSize: 13, outline: "none", resize: "vertical",
                    fontFamily: "inherit", boxSizing: "border-box",
                  }}
                />
              </div>
            </GlowCard>
          )}

          {step === 1 && (
            <GlowCard>
              <SectionTitle icon="⚡">Skills & Certifications</SectionTitle>
              <div style={{ marginBottom: 16 }}>
                <label style={{ color: THEME.textDim, fontSize: 12, fontWeight: 600, display: "block", marginBottom: 6 }}>
                  Technical Skills (comma-separated)
                </label>
                <textarea
                  value={form.skills}
                  onChange={(e) => update("skills", e.target.value)}
                  placeholder="Python, React, Docker, AWS, PostgreSQL, FastAPI, Git..."
                  style={{
                    width: "100%", height: 100, padding: "10px 12px", borderRadius: 8,
                    background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
                    color: THEME.text, fontSize: 13, outline: "none", resize: "vertical",
                    fontFamily: "inherit", boxSizing: "border-box",
                  }}
                />
              </div>
              <div>
                <label style={{ color: THEME.textDim, fontSize: 12, fontWeight: 600, display: "block", marginBottom: 6 }}>
                  Certifications (comma-separated)
                </label>
                <input
                  value={form.certifications}
                  onChange={(e) => update("certifications", e.target.value)}
                  placeholder="AWS Solutions Architect, Google Cloud Professional..."
                  style={{
                    width: "100%", padding: "10px 12px", borderRadius: 8,
                    background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
                    color: THEME.text, fontSize: 13, outline: "none", boxSizing: "border-box",
                  }}
                />
              </div>
            </GlowCard>
          )}

          {step === 2 && (
            <GlowCard>
              <SectionTitle icon="💼">Work Experience</SectionTitle>
              {form.work_experience.map((exp, i) => (
                <div key={i} style={{
                  padding: 16, borderRadius: 10, marginBottom: 14,
                  background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
                }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
                    {[
                      { label: "Job Title", key: "title", placeholder: "Senior Engineer" },
                      { label: "Company", key: "company", placeholder: "TechCorp" },
                      { label: "Duration", key: "duration", placeholder: "2021 - Present" },
                    ].map(({ label, key, placeholder }) => (
                      <div key={key}>
                        <label style={{ color: THEME.textDim, fontSize: 11, fontWeight: 600, display: "block", marginBottom: 4 }}>{label}</label>
                        <input
                          value={exp[key]}
                          onChange={(e) => updateArr("work_experience", i, key, e.target.value)}
                          placeholder={placeholder}
                          style={{
                            width: "100%", padding: "8px 10px", borderRadius: 7,
                            background: THEME.surface, border: `1px solid ${THEME.border}`,
                            color: THEME.text, fontSize: 12, outline: "none", boxSizing: "border-box",
                          }}
                        />
                      </div>
                    ))}
                  </div>
                  <label style={{ color: THEME.textDim, fontSize: 11, fontWeight: 600, display: "block", marginBottom: 4 }}>Key Achievement</label>
                  <input
                    value={exp.description[0] || ""}
                    onChange={(e) => {
                      const arr = [...form.work_experience];
                      arr[i].description = [e.target.value];
                      setForm((p) => ({ ...p, work_experience: arr }));
                    }}
                    placeholder="Built APIs handling 1M+ requests/day, reducing latency by 40%"
                    style={{
                      width: "100%", padding: "8px 10px", borderRadius: 7,
                      background: THEME.surface, border: `1px solid ${THEME.border}`,
                      color: THEME.text, fontSize: 12, outline: "none", boxSizing: "border-box",
                    }}
                  />
                </div>
              ))}
              <button
                onClick={() => addItem("work_experience", { company: "", title: "", duration: "", description: [""] })}
                style={{
                  padding: "8px 16px", borderRadius: 8, background: "transparent",
                  border: `1px dashed ${THEME.accent}`, color: THEME.accent,
                  cursor: "pointer", fontSize: 13,
                }}
              >
                + Add Experience
              </button>
            </GlowCard>
          )}

          {step === 3 && (
            <GlowCard>
              <SectionTitle icon="🎓">Education</SectionTitle>
              {form.education.map((edu, i) => (
                <div key={i} style={{
                  padding: 16, borderRadius: 10, marginBottom: 14,
                  background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
                }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                    {[
                      { label: "Institution", key: "institution", placeholder: "UC Berkeley" },
                      { label: "Degree", key: "degree", placeholder: "B.Sc Computer Science" },
                      { label: "Graduation Year", key: "year", placeholder: "2020" },
                    ].map(({ label, key, placeholder }) => (
                      <div key={key}>
                        <label style={{ color: THEME.textDim, fontSize: 11, fontWeight: 600, display: "block", marginBottom: 4 }}>{label}</label>
                        <input
                          value={edu[key]}
                          onChange={(e) => updateArr("education", i, key, e.target.value)}
                          placeholder={placeholder}
                          style={{
                            width: "100%", padding: "8px 10px", borderRadius: 7,
                            background: THEME.surface, border: `1px solid ${THEME.border}`,
                            color: THEME.text, fontSize: 12, outline: "none", boxSizing: "border-box",
                          }}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
              <button
                onClick={() => addItem("education", { institution: "", degree: "", year: "" })}
                style={{
                  padding: "8px 16px", borderRadius: 8, background: "transparent",
                  border: `1px dashed ${THEME.accent}`, color: THEME.accent,
                  cursor: "pointer", fontSize: 13,
                }}
              >
                + Add Education
              </button>
            </GlowCard>
          )}

          {step === 4 && (
            <GlowCard>
              <SectionTitle icon="🚀">Projects</SectionTitle>
              {form.projects.map((proj, i) => (
                <div key={i} style={{
                  padding: 16, borderRadius: 10, marginBottom: 14,
                  background: THEME.surfaceHigh, border: `1px solid ${THEME.borderHigh}`,
                }}>
                  {[
                    { label: "Project Name", key: "name", placeholder: "AI Chat Platform" },
                    { label: "Description", key: "description", placeholder: "Built a real-time chat app using GPT-4 with 10K+ users" },
                    { label: "Technologies (comma-separated)", key: "technologies", placeholder: "React, Python, OpenAI, PostgreSQL" },
                  ].map(({ label, key, placeholder }) => (
                    <div key={key} style={{ marginBottom: 8 }}>
                      <label style={{ color: THEME.textDim, fontSize: 11, fontWeight: 600, display: "block", marginBottom: 4 }}>{label}</label>
                      <input
                        value={proj[key]}
                        onChange={(e) => updateArr("projects", i, key, e.target.value)}
                        placeholder={placeholder}
                        style={{
                          width: "100%", padding: "8px 10px", borderRadius: 7,
                          background: THEME.surface, border: `1px solid ${THEME.border}`,
                          color: THEME.text, fontSize: 12, outline: "none", boxSizing: "border-box",
                        }}
                      />
                    </div>
                  ))}
                </div>
              ))}
              <button
                onClick={() => addItem("projects", { name: "", description: "", technologies: "" })}
                style={{
                  padding: "8px 16px", borderRadius: 8, background: "transparent",
                  border: `1px dashed ${THEME.accent}`, color: THEME.accent,
                  cursor: "pointer", fontSize: 13,
                }}
              >
                + Add Project
              </button>
            </GlowCard>
          )}

          {step === 5 && (
            <GlowCard>
              <SectionTitle icon="🎨">Choose Template</SectionTitle>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                {TEMPLATES.map((t) => (
                  <div
                    key={t.id}
                    onClick={() => setTemplate(t.id)}
                    style={{
                      padding: 20, borderRadius: 12, cursor: "pointer",
                      background: template === t.id ? THEME.accentGlow : THEME.surfaceHigh,
                      border: `2px solid ${template === t.id ? THEME.accent : THEME.borderHigh}`,
                      transition: "all 0.15s",
                    }}
                  >
                    <div style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: t.color, marginBottom: 10,
                    }}/>
                    <div style={{ color: THEME.text, fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{t.name}</div>
                    <div style={{ color: THEME.textMuted, fontSize: 12 }}>{t.desc}</div>
                    {template === t.id && (
                      <div style={{ color: THEME.accent, fontSize: 11, marginTop: 8, fontWeight: 600 }}>✓ Selected</div>
                    )}
                  </div>
                ))}
              </div>
            </GlowCard>
          )}

          {generated && (
            <GlowCard style={{ marginTop: 20 }}>
              <SectionTitle icon="✅">Resume Generated!</SectionTitle>
              <div style={{ marginBottom: 16, display: "flex", gap: 10 }}>
                <a
                  href={`${API_BASE}/builder/download/${generated.filename}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    padding: "10px 20px", borderRadius: 8,
                    background: `linear-gradient(135deg, ${THEME.success}, ${THEME.success}99)`,
                    color: "#fff", textDecoration: "none", fontSize: 13, fontWeight: 700,
                  }}
                >
                  ⬇ Download Resume
                </a>
              </div>
              <div style={{
                background: "#fff", borderRadius: 10, padding: 0, overflow: "hidden",
                maxHeight: 400, overflowY: "auto",
                border: `1px solid ${THEME.border}`,
              }}>
                <iframe
                  srcDoc={generated.preview_html}
                  style={{ width: "100%", height: 400, border: "none" }}
                  title="Resume Preview"
                />
              </div>
            </GlowCard>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main App ───────────────────────────────────────────────────────────────────
export default function App() {
  const [activeTab, setActiveTab] = useState("upload");
  const [analysisData, setAnalysisData] = useState(null);

  const TABS = [
    { id: "upload", label: "Upload" },
    { id: "analysis", label: "Analysis" },
    { id: "jobs", label: "Job Match"},
    { id: "gaps", label: "Skill Gap" },
    { id: "builder", label: "Builder" },
  ];

  return (
    <div style={{
      minHeight: "100vh",
      background: THEME.bg,
      color: THEME.text,
      fontFamily: "'DM Sans', 'Segoe UI', system-ui, sans-serif",
    }}>
      {/* Global styles */}
      <style>{`
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: ${THEME.surface}; }
        ::-webkit-scrollbar-thumb { background: ${THEME.borderHigh}; border-radius: 99px; }
        input::placeholder, textarea::placeholder { color: ${THEME.textMuted}; }
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
        button:hover { opacity: 0.9; }
      `}</style>

      {/* Navbar */}
      <nav style={{
        borderBottom: `1px solid ${THEME.border}`,
        padding: "0 32px",
        display: "flex", alignItems: "center", gap: 32,
        height: 60,
        background: THEME.surface + "DD",
        backdropFilter: "blur(12px)",
        position: "sticky", top: 0, zIndex: 100,
      }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, flex: "0 0 auto" }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: `linear-gradient(135deg, ${THEME.accent}, ${THEME.accentHover})`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 16,
          }}>✦</div>
          <span style={{ fontWeight: 800, fontSize: 16, color: THEME.text }}>
            Smart <span style={{ color: THEME.accent }}>AI</span> Resume <span style={{ color: THEME.accent }}>Analyzer</span>
          </span>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 4, flex: 1 }}>
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              style={{
                padding: "6px 16px", borderRadius: 8,
                background: activeTab === t.id ? THEME.accentGlow : "transparent",
                border: activeTab === t.id ? `1px solid ${THEME.accent}44` : "1px solid transparent",
                color: activeTab === t.id ? THEME.accent : THEME.textMuted,
                cursor: "pointer", fontSize: 13, fontWeight: activeTab === t.id ? 700 : 400,
                display: "flex", alignItems: "center", gap: 6,
                transition: "all 0.15s",
              }}
            >
              {t.icon} {t.label}
              {t.id === "analysis" && analysisData && (
                <span style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: THEME.success, display: "inline-block",
                }}/>
              )}
            </button>
          ))}
        </div>

        {analysisData && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: THEME.success }}/>
            <span style={{ color: THEME.textMuted }}>{analysisData.filename}</span>
            <Badge color={THEME.success}>{analysisData.score?.total_score}/100</Badge>
          </div>
        )}
      </nav>

      {/* Main content */}
      <main style={{ padding: "32px 32px 80px" }}>
        {activeTab === "upload" && (
          <UploadPage onAnalyzed={setAnalysisData} setActiveTab={setActiveTab} />
        )}
        {activeTab === "analysis" && (
          <AnalysisPage data={analysisData} />
        )}
        {activeTab === "jobs" && (
          <JobMatchPage analysisData={analysisData} />
        )}
        {activeTab === "gaps" && (
          <SkillGapPage analysisData={analysisData} />
        )}
        {activeTab === "builder" && (
          <BuilderPage />
        )}
      </main>
    </div>
  );
}
