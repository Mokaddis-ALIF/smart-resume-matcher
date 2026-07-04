import { useState, useEffect } from "react";
import { listJobs, getResults, triggerMatching } from "../services/api";

export default function Results() {
  const [jobs, setJobs]                 = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [results, setResults]           = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [matching, setMatching]         = useState(false);
  const [matchMessage, setMatchMessage] = useState("");

  useEffect(() => {
    listJobs().then(data => setJobs(data.jobs || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedJobId) fetchResults();
  }, [selectedJobId]);

  const fetchResults = async () => {
    try {
      const data = await getResults(selectedJobId);
      setResults(data);
    } catch (err) { console.error(err); }
  };

  const handleMatch = async () => {
    setMatching(true);
    setMatchMessage("Scoring all resumes against job requirements...");
    try {
      const data = await triggerMatching(selectedJobId);
      setMatchMessage(data.message);
      fetchResults();
    } catch (err) {
      setMatchMessage("Matching failed: " + err.message);
    } finally {
      setMatching(false);
      setTimeout(() => setMatchMessage(""), 6000);
    }
  };

  const selectedJob = jobs.find(j => j._id === selectedJobId);

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2>Match Results</h2>
          <p>AI-scored and ranked candidates for your job posting</p>
        </div>
        {selectedJobId && (
          <button
            className={`btn ${matching ? "btn-secondary" : "btn-success"}`}
            onClick={handleMatch}
            disabled={matching}
            style={{ fontSize: 13 }}
          >
            {matching ? "⏳ Scoring..." : "▶ Run Matching"}
          </button>
        )}
      </div>

      {/* Job selector */}
      <div className="card" style={{ marginBottom: 16 }}>
        <label style={{ fontSize: 12, fontWeight: 600, color: "#475569", display: "block", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Select Job Posting
        </label>
        <select
          className="input"
          value={selectedJobId}
          onChange={e => { setSelectedJobId(e.target.value); setResults(null); setSelectedResult(null); }}
        >
          <option value="">— Choose a job to view candidates —</option>
          {jobs.map(job => (
            <option key={job._id} value={job._id}>
              {job.reference ? `${job.reference}  ` : ""}{job.title}
            </option>
          ))}
        </select>
      </div>

      {matchMessage && (
        <div style={{ padding: "11px 16px", borderRadius: 8, background: "#eef2ff", color: "#4338ca", fontSize: 13, marginBottom: 16, fontWeight: 500, border: "1px solid #c7d2fe" }}>
          ℹ️ {matchMessage}
        </div>
      )}

      {results ? (
        <>
          {/* Summary strip */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
            <SummaryCard count={results.summary.highly_qualified} label="Highly Qualified" icon="✅" color="#059669" bg="#d1fae5" border="#6ee7b7" />
            <SummaryCard count={results.summary.qualified}        label="Qualified"        icon="⚡" color="#d97706" bg="#fef3c7" border="#fcd34d" />
            <SummaryCard count={results.summary.not_qualified}    label="Not Qualified"    icon="✗"  color="#dc2626" bg="#fee2e2" border="#fca5a5" />
          </div>

          {selectedJob && (
            <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 14 }}>
              Showing {results.total} candidate{results.total !== 1 ? "s" : ""} ranked for{" "}
              <strong style={{ color: "#475569" }}>{selectedJob.title}</strong>
            </div>
          )}

          {/* List + detail panel */}
          <div style={{ display: "grid", gridTemplateColumns: selectedResult ? "1fr 1fr" : "1fr", gap: 16, alignItems: "start" }}>
            {/* Ranked list */}
            <div>
              {results.results.length === 0 ? (
                <div className="card empty-state">
                  <div className="empty-state-icon">📄</div>
                  <h4>No results yet</h4>
                  <p>Click "Run Matching" to score all uploaded CVs</p>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
                  {results.results.map((r, rank) => (
                    <CandidateCard
                      key={r._id}
                      result={r}
                      rank={rank}
                      selected={selectedResult?._id === r._id}
                      onClick={() => setSelectedResult(selectedResult?._id === r._id ? null : r)}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Detail breakdown */}
            {selectedResult && (
              <div className="card" style={{ position: "sticky", top: 20, maxHeight: "calc(100vh - 120px)", overflowY: "auto" }}>
                <ScoreDetail result={selectedResult} onClose={() => setSelectedResult(null)} />
              </div>
            )}
          </div>
        </>
      ) : selectedJobId ? (
        <div className="card empty-state">
          <div className="empty-state-icon">🏆</div>
          <h4>No results yet</h4>
          <p>Click "Run Matching" to start scoring candidates</p>
        </div>
      ) : (
        <div className="card empty-state">
          <div className="empty-state-icon">💼</div>
          <h4>Select a job posting above</h4>
          <p>Then run matching to see ranked candidates</p>
        </div>
      )}
    </div>
  );
}

/* ─── Candidate row card ─── */
function CandidateCard({ result, rank, selected, onClick }) {
  const cat = catStyle(result.category);
  return (
    <div
      onClick={onClick}
      style={{
        display: "flex", alignItems: "center", gap: 12,
        padding: "12px 16px", borderRadius: 10, cursor: "pointer",
        background: selected ? "#fafbff" : "#fff",
        border: `1px solid ${selected ? "#4f46e5" : "#e2e8f0"}`,
        borderLeft: `4px solid ${cat.color}`,
        boxShadow: selected ? "0 0 0 2px rgba(79,70,229,0.12)" : "0 1px 3px rgba(0,0,0,0.05)",
        transition: "all 0.13s ease",
      }}
      onMouseEnter={e => { if (!selected) e.currentTarget.style.boxShadow = "0 3px 10px rgba(0,0,0,0.08)"; }}
      onMouseLeave={e => { if (!selected) e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.05)"; }}
    >
      {/* Rank */}
      <div style={{
        width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
        background: rank < 3 ? cat.color : "#f1f5f9",
        color: rank < 3 ? "#fff" : "#475569",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 12, fontWeight: 700,
      }}>
        {rank + 1}
      </div>

      {/* Avatar initial */}
      <div style={{
        width: 36, height: 36, borderRadius: "50%", flexShrink: 0,
        background: `${cat.color}18`, color: cat.color,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 14, fontWeight: 700,
      }}>
        {(result.candidate_name || result.filename || "?")[0].toUpperCase()}
      </div>

      {/* Name + file */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13.5, fontWeight: 700, color: "#0f172a", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {result.candidate_name || result.filename}
        </div>
        <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {result.filename}
        </div>
      </div>

      {/* Category badge */}
      <span style={{
        fontSize: 11, padding: "3px 10px", borderRadius: 20,
        background: cat.bg, color: cat.color,
        border: `1px solid ${cat.border}`,
        fontWeight: 600, flexShrink: 0, whiteSpace: "nowrap",
      }}>
        {cat.label}
      </span>

      {/* Score */}
      <div style={{
        fontSize: 22, fontWeight: 800, color: cat.color,
        width: 52, textAlign: "right", flexShrink: 0, letterSpacing: "-0.02em",
      }}>
        {result.overall_score}
      </div>
    </div>
  );
}

/* ─── Score breakdown detail panel ─── */
function ScoreDetail({ result, onClose }) {
  const cat = catStyle(result.category);

  return (
    <>
      {/* Top bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: "#475569" }}>Score Breakdown</span>
        <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 18, color: "#94a3b8", lineHeight: 1 }}>✕</button>
      </div>

      {/* Candidate hero */}
      <div style={{
        textAlign: "center", paddingBottom: 20, marginBottom: 20,
        borderBottom: "1px solid #e2e8f0",
      }}>
        <div style={{
          width: 56, height: 56, borderRadius: "50%", margin: "0 auto 10px",
          background: `${cat.color}18`, color: cat.color,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 22, fontWeight: 800,
        }}>
          {(result.candidate_name || result.filename || "?")[0].toUpperCase()}
        </div>
        <div style={{ fontSize: 16, fontWeight: 700, color: "#0f172a" }}>{result.candidate_name}</div>
        <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 10, alignItems: "center" }}>
          <div style={{ fontSize: 40, fontWeight: 800, color: cat.color, lineHeight: 1 }}>
            {result.overall_score}
          </div>
          <div style={{ textAlign: "left" }}>
            <div style={{ fontSize: 12, color: "#94a3b8" }}>/ 100</div>
            <span style={{
              fontSize: 11, padding: "3px 10px", borderRadius: 20, fontWeight: 600,
              background: cat.bg, color: cat.color, border: `1px solid ${cat.border}`,
            }}>
              {cat.label}
            </span>
          </div>
        </div>
      </div>

      {/* Explanation */}
      {result.explanation && (
        <div style={{ background: "#f8fafc", borderRadius: 8, padding: "10px 14px", marginBottom: 16, fontSize: 12.5, lineHeight: 1.7, color: "#475569", border: "1px solid #e2e8f0" }}>
          {result.explanation}
        </div>
      )}

      {/* Scoring dimensions */}
      {result.score_breakdown && (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {Object.entries(result.score_breakdown).map(([key, data]) => (
            <ScoreDimension key={key} dimKey={key} data={data} />
          ))}
        </div>
      )}

      {/* ML predictions */}
      {result.ml_predictions && Object.keys(result.ml_predictions).length > 0 && (
        <div style={{ marginTop: 20, paddingTop: 16, borderTop: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#475569", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>
            ML Category Prediction
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
            {Object.entries(result.ml_predictions).map(([model, pred]) => (
              <div key={model} style={{
                display: "flex", justifyContent: "space-between", alignItems: "center",
                padding: "7px 12px", borderRadius: 7, background: "#f8fafc",
                border: "1px solid #e2e8f0", fontSize: 12.5,
              }}>
                <span style={{ color: "#475569", fontWeight: 500 }}>{model}</span>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span style={{ padding: "2px 9px", borderRadius: 20, background: "#eef2ff", color: "#4f46e5", fontSize: 11, fontWeight: 600 }}>
                    {pred.category}
                  </span>
                  {pred.confidence && (
                    <span style={{ fontSize: 11, color: "#94a3b8", width: 38, textAlign: "right" }}>{pred.confidence}%</span>
                  )}
                </div>
              </div>
            ))}
          </div>
          <p style={{ fontSize: 10.5, color: "#94a3b8", marginTop: 8 }}>
            Predicted job category based on resume text · AI Resume Screening dataset (4 IT roles)
          </p>
        </div>
      )}
    </>
  );
}

/* ─── Single scoring dimension row ─── */
const DIM_META = {
  skills:     { icon: "⚙️", label: "Technical Skills" },
  experience: { icon: "📅", label: "Work Experience" },
  education:  { icon: "🎓", label: "Education" },
  projects:   { icon: "🔧", label: "Projects" },
};

function ScoreDimension({ dimKey, data }) {
  const meta   = DIM_META[dimKey] || { icon: "•", label: dimKey };
  const pct    = data.score || 0;
  const barClr = pct >= 75 ? "#059669" : pct >= 50 ? "#d97706" : "#dc2626";

  return (
    <div style={{ padding: "12px 14px", borderRadius: 9, background: "#f8fafc", border: "1px solid #e2e8f0" }}>
      {/* Header row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <span style={{ fontSize: 13, fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
          {meta.icon} {meta.label}
        </span>
        <span style={{ fontSize: 12, color: "#94a3b8" }}>
          {pct}/100 × {(data.weight * 100).toFixed(0)}% =&nbsp;
          <strong style={{ color: barClr }}>{data.weighted_score}</strong>
        </span>
      </div>

      {/* Progress bar */}
      <div className="progress-track" style={{ marginBottom: 8 }}>
        <div className="progress-fill" style={{ width: `${pct}%`, background: barClr }} />
      </div>

      {/* Dimension-specific detail */}
      {dimKey === "skills" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
          {data.matched?.length > 0 && (
            <ChipRow label="Matched" chips={data.matched} chipColor="#059669" chipBg="#d1fae5" />
          )}
          {data.missing?.length > 0 && (
            <ChipRow label="Missing" chips={data.missing} chipColor="#dc2626" chipBg="#fee2e2" />
          )}
          {data.preferred_matched?.length > 0 && (
            <ChipRow label="Preferred ✓" chips={data.preferred_matched} chipColor="#4f46e5" chipBg="#eef2ff" />
          )}
        </div>
      )}

      {dimKey === "experience" && (
        <div style={{ fontSize: 12, color: "#475569" }}>
          {data.candidate_years}y experience
          {data.required_years > 0 && <span style={{ color: "#94a3b8" }}> (requires {data.required_years}y)</span>}
          {data.relevant_roles?.length > 0 && (
            <div style={{ marginTop: 4, color: "#94a3b8" }}>Roles: {data.relevant_roles.join(", ")}</div>
          )}
        </div>
      )}

      {dimKey === "education" && (
        <div style={{ fontSize: 12 }}>
          <span style={{ color: "#475569" }}>Has: <strong>{data.candidate_level || "—"}</strong></span>
          <span style={{ color: "#94a3b8" }}> · Requires: {data.required_level}</span>
          {data.field_match && <span style={{ color: "#059669", marginLeft: 6 }}>✓ IT field match</span>}
          {data.it_required && !data.field_match && data.candidate_level !== "none" && (
            <span style={{ color: "#dc2626", marginLeft: 6 }}>✗ IT field required</span>
          )}
        </div>
      )}

      {dimKey === "projects" && (
        <div style={{ fontSize: 12, color: "#475569" }}>
          {data.relevant_projects?.length > 0
            ? <span>Projects: <strong>{data.relevant_projects.join(", ")}</strong></span>
            : <span style={{ color: "#94a3b8" }}>No directly relevant projects detected</span>
          }
          {data.tech_overlap?.length > 0 && (
            <ChipRow label="Tech overlap" chips={data.tech_overlap} chipColor="#7c3aed" chipBg="#f5f3ff" />
          )}
        </div>
      )}
    </div>
  );
}

function ChipRow({ label, chips, chipColor, chipBg }) {
  return (
    <div style={{ display: "flex", gap: 5, flexWrap: "wrap", alignItems: "center" }}>
      <span style={{ fontSize: 10.5, color: "#94a3b8", flexShrink: 0 }}>{label}:</span>
      {chips.map((c, i) => (
        <span key={i} style={{
          fontSize: 10.5, padding: "2px 8px", borderRadius: 20,
          background: chipBg, color: chipColor, fontWeight: 600,
        }}>{c}</span>
      ))}
    </div>
  );
}

function SummaryCard({ count, label, icon, color, bg, border }) {
  return (
    <div className="card" style={{ textAlign: "center", background: bg, border: `1px solid ${border}`, padding: "18px 12px" }}>
      <div style={{ fontSize: 26 }}>{icon}</div>
      <div style={{ fontSize: 36, fontWeight: 800, color, lineHeight: 1, marginTop: 4 }}>{count}</div>
      <div style={{ fontSize: 12, color, fontWeight: 600, marginTop: 4 }}>{label}</div>
    </div>
  );
}

/* ─── Shared helpers ─── */
function catStyle(cat) {
  if (cat === "highly_qualified") return { label: "Highly Qualified", color: "#059669", bg: "#d1fae5", border: "#6ee7b7" };
  if (cat === "qualified")        return { label: "Qualified",        color: "#d97706", bg: "#fef3c7", border: "#fcd34d" };
  return                                 { label: "Not Qualified",    color: "#dc2626", bg: "#fee2e2", border: "#fca5a5" };
}
