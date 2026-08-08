import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { checkHealth, listJobs, getEvaluationResults } from "../services/api";

const STEPS = [
  { num: "1", icon: "💼", title: "Post a Job", desc: "Define the role, required skills, and experience", to: "/jobs", cta: "Go to Jobs" },
  { num: "2", icon: "📄", title: "Upload CVs", desc: "Drag & drop candidate resumes — PDF or DOCX", to: "/resumes", cta: "Upload CVs" },
  { num: "3", icon: "🏆", title: "View Rankings", desc: "Instantly see ranked candidates with scores", to: "/results", cta: "View Results" },
];

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [evalData, setEvalData] = useState(null);
  const [totalResumes, setTotalResumes] = useState(0);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: "error", database: "error" }));

    listJobs()
      .then(data => {
        setJobs(data.jobs || []);
        const total = (data.jobs || []).reduce((s, j) => s + (j.matched_count || 0), 0);
        setTotalResumes(total);
      })
      .catch(() => { });

    getEvaluationResults().then(setEvalData).catch(() => { });
  }, []);

  const apiOk = health?.status === "running";
  const dbOk = health?.database === "connected";
  const d1 = evalData?.dataset1;
  const bestModel = d1?.results
    ? Object.entries(d1.results).reduce((a, b) => a[1].f1_score > b[1].f1_score ? a : b)
    : null;

  return (
    <div>
      {/* Header */}
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Dashboard</h2>
          <p>Overview of your hiring pipeline</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <StatusPill ok={apiOk} label="API" loading={!health} />
          <StatusPill ok={dbOk} label="DB" loading={!health} />
        </div>
      </div>

      {/* KPI cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 24 }}>
        <KpiCard icon="💼" label="Open Jobs" value={jobs.length} accent="#4f46e5" />
        <KpiCard icon="📄" label="CVs Processed" value={totalResumes} accent="#059669" />
        <KpiCard icon="🏆" label="Best Model F1" value={bestModel ? `${bestModel[1].f1_score}%` : "—"} accent="#7c3aed" />
        <KpiCard icon="🤖" label="NLP + ML" value="Active" accent="#0891b2" />
      </div>

      {/* Workflow guide */}
      <div className="card" style={{ marginBottom: 22, background: "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)", border: "none" }}>
        <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 11, fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 16 }}>
          HOW IT WORKS — 3 STEPS TO HIRE FASTER
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr auto 1fr", gap: 12, alignItems: "center" }}>
          {STEPS.map((step, i) => (
            <>
              <StepCard key={step.num} step={step} />
              {i < STEPS.length - 1 && (
                <div key={`arrow-${i}`} style={{ color: "rgba(255,255,255,0.25)", fontSize: 20, textAlign: "center" }}>›</div>
              )}
            </>
          ))}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {/* Recent jobs */}
        <div className="card">
          <div className="card-title">
            💼 Recent Job Postings
            <Link to="/jobs" style={{ marginLeft: "auto", fontSize: 12, color: "#4f46e5", textDecoration: "none", fontWeight: 500 }}>
              View all →
            </Link>
          </div>
          {jobs.length === 0 ? (
            <div className="empty-state" style={{ padding: "28px 0" }}>
              <div className="empty-state-icon">💼</div>
              <p>No jobs yet — create your first posting</p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {jobs.slice(0, 6).map(job => (
                <div key={job._id} style={{
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  padding: "9px 12px", borderRadius: 8, background: "#f8fafc",
                  border: "1px solid #e2e8f0",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    {job.reference && (
                      <span style={{ fontSize: 10, padding: "2px 7px", borderRadius: 4, background: "#e2e8f0", color: "#64748b", fontWeight: 700, fontFamily: "monospace" }}>
                        {job.reference}
                      </span>
                    )}
                    <span style={{ fontSize: 13, fontWeight: 600, color: "#0f172a" }}>{job.title}</span>
                  </div>
                  <span style={{
                    fontSize: 11, padding: "2px 9px", borderRadius: 20,
                    background: job.matched_count > 0 ? "#d1fae5" : "#f1f5f9",
                    color: job.matched_count > 0 ? "#059669" : "#94a3b8",
                    fontWeight: 600,
                  }}>
                    {job.matched_count || 0} uploaded
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ML model summary */}
        <div className="card">
          <div className="card-title">
            🤖 ML Model Performance (D1 — 4 IT Roles)
            <Link to="/evaluation" style={{ marginLeft: "auto", fontSize: 12, color: "#4f46e5", textDecoration: "none", fontWeight: 500 }}>
              Full report →
            </Link>
          </div>
          {!d1 ? (
            <div className="empty-state" style={{ padding: "28px 0" }}>
              <div className="empty-state-icon">📈</div>
              <p>Models not trained yet</p>
              <Link to="/evaluation" className="btn btn-primary" style={{ marginTop: 12, textDecoration: "none", fontSize: 12 }}>
                Train Models
              </Link>
            </div>
          ) : (
            <div>
              {bestModel && (
                <div style={{ padding: "10px 14px", borderRadius: 8, background: "#f0fdf4", border: "1px solid #a7f3d0", marginBottom: 14, display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 20 }}>🏆</span>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "#059669" }}>Best: {bestModel[0]}</div>
                    <div style={{ fontSize: 11, color: "#6b7280" }}>{bestModel[1].f1_score}% F1 · {bestModel[1].accuracy}% Accuracy</div>
                  </div>
                </div>
              )}
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {Object.entries(d1.results).map(([name, m]) => (
                  <div key={name} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 12, width: 108, color: "#475569", flexShrink: 0 }}>{name}</span>
                    <div className="progress-track">
                      <div className="progress-fill" style={{
                        width: `${m.f1_score}%`,
                        background: name === bestModel?.[0] ? "#059669" : "#94a3b8",
                      }} />
                    </div>
                    <span style={{ fontSize: 12, fontWeight: 700, width: 46, textAlign: "right", color: name === bestModel?.[0] ? "#059669" : "#475569" }}>
                      {m.f1_score}%
                    </span>
                  </div>
                ))}
              </div>
              <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 10 }}>
                Trained on {d1.dataset_size?.toLocaleString()} resumes · {d1.categories?.length} categories
              </div>
            </div>
          )}
        </div>
      </div>

      {/* System stack */}
      <div className="card">
        <div className="card-title">⚙️ System Architecture</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, fontSize: 13 }}>
          {[
            { color: "#4f46e5", label: "Backend", items: ["Python · Flask", "MongoDB · PyMongo", "PyMuPDF · python-docx"] },
            { color: "#059669", label: "NLP / ML", items: ["spaCy NER", "BERT Sentence Transformers", "scikit-learn (SVM, RF, KNN, NB)"] },
            { color: "#0891b2", label: "Frontend", items: ["React + Vite", "React Router v7", "REST API integration"] },
          ].map(col => (
            <div key={col.label}>
              <div style={{ fontWeight: 700, marginBottom: 8, color: col.color, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                {col.label}
              </div>
              {col.items.map(item => (
                <div key={item} style={{ color: "#475569", padding: "3px 0", display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ width: 4, height: 4, borderRadius: "50%", background: col.color, flexShrink: 0, display: "inline-block" }} />
                  {item}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function KpiCard({ icon, label, value, accent }) {
  return (
    <div className="card" style={{ borderTop: `3px solid ${accent}`, padding: "16px 20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
        <span style={{ fontSize: 22 }}>{icon}</span>
        <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 20, background: `${accent}15`, color: accent, fontWeight: 600 }}>
          Live
        </span>
      </div>
      <div style={{ fontSize: 26, fontWeight: 800, color: "#0f172a", lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 4 }}>{label}</div>
    </div>
  );
}

function StatusPill({ ok, label, loading }) {
  const bg = loading ? "#f1f5f9" : ok ? "#d1fae5" : "#fee2e2";
  const color = loading ? "#94a3b8" : ok ? "#059669" : "#dc2626";
  const dot = loading ? "⏳" : ok ? "●" : "●";
  return (
    <span style={{ fontSize: 11, padding: "4px 10px", borderRadius: 20, background: bg, color, fontWeight: 600, display: "inline-flex", alignItems: "center", gap: 4 }}>
      {dot} {label}
    </span>
  );
}

function StepCard({ step }) {
  return (
    <Link to={step.to} style={{ textDecoration: "none" }}>
      <div style={{
        background: "rgba(255,255,255,0.06)", borderRadius: 10,
        padding: "14px 16px", border: "1px solid rgba(255,255,255,0.08)",
        transition: "background 0.15s",
        cursor: "pointer",
      }}
        onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.1)"}
        onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.06)"}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
          <span style={{
            width: 22, height: 22, borderRadius: "50%", background: "#4f46e5",
            color: "#fff", fontSize: 11, fontWeight: 700,
            display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
          }}>{step.num}</span>
          <span style={{ fontSize: 18 }}>{step.icon}</span>
          <span style={{ fontSize: 13, fontWeight: 700, color: "#fff" }}>{step.title}</span>
        </div>
        <p style={{ fontSize: 11.5, color: "rgba(255,255,255,0.45)", lineHeight: 1.5, marginBottom: 10 }}>{step.desc}</p>
        <span style={{ fontSize: 11, color: "#a5b4fc", fontWeight: 600 }}>{step.cta} →</span>
      </div>
    </Link>
  );
}
