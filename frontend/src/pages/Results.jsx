import { useState, useEffect } from "react";
import { listJobs, getResults, triggerMatching } from "../services/api";

export default function Results() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [results, setResults] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [matching, setMatching] = useState(false);
  const [matchMessage, setMatchMessage] = useState("");

  useEffect(() => {
    listJobs().then(data => setJobs(data.jobs)).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedJobId) fetchResults();
  }, [selectedJobId]);

  const fetchResults = async () => {
    try {
      const data = await getResults(selectedJobId);
      setResults(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleMatch = async () => {
    setMatching(true);
    setMatchMessage("Scoring resumes...");
    try {
      const data = await triggerMatching(selectedJobId);
      setMatchMessage(data.message);
      fetchResults();
    } catch (err) {
      setMatchMessage("Matching failed: " + err.message);
    } finally {
      setMatching(false);
      setTimeout(() => setMatchMessage(""), 5000);
    }
  };

  const categoryStyle = (cat) => {
    if (cat === "highly_qualified") return { bg: "#d1fae5", text: "#059669", label: "Highly Qualified" };
    if (cat === "qualified") return { bg: "#fef3c7", text: "#d97706", label: "Qualified" };
    return { bg: "#fee2e2", text: "#dc2626", label: "Not Qualified" };
  };

  const scoreColor = (score) => {
    if (score >= 75) return "#059669";
    if (score >= 50) return "#d97706";
    return "#dc2626";
  };

  return (
    <div>
      <div className="page-header">
        <h2>Match Results</h2>
        <p>Score and rank candidates against job requirements</p>
      </div>

      {/* Job selector + match button */}
      <div className="card" style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "flex-end" }}>
        <div style={{ flex: 1 }}>
          <label style={{ fontSize: 13, fontWeight: 500, color: "#374151", display: "block", marginBottom: 6 }}>
            Select a Job Posting
          </label>
          <select
            style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid #d1d5db", fontSize: 14 }}
            value={selectedJobId}
            onChange={e => { setSelectedJobId(e.target.value); setResults(null); setSelectedResult(null); }}
          >
            <option value="">-- Choose a job --</option>
            {jobs.map(job => (
              <option key={job._id} value={job._id}>{job.reference ? `${job.reference}: ` : ""}{job.title}</option>
            ))}
          </select>
        </div>
        {selectedJobId && (
          <button className="btn btn-primary" onClick={handleMatch} disabled={matching} style={{ whiteSpace: "nowrap" }}>
            {matching ? "Scoring..." : "Run Matching"}
          </button>
        )}
      </div>

      {matchMessage && (
        <div style={{ padding: "10px 16px", borderRadius: 8, background: "#eef2ff", color: "#4338ca", fontSize: 13, marginBottom: 16, fontWeight: 500 }}>
          {matchMessage}
        </div>
      )}

      {results && (
        <>
          {/* Summary cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
            {[
              { key: "highly_qualified", icon: "✅", label: "Highly Qualified" },
              { key: "qualified", icon: "⚡", label: "Qualified" },
              { key: "not_qualified", icon: "❌", label: "Not Qualified" },
            ].map(({ key, icon, label }) => {
              const style = categoryStyle(key);
              return (
                <div key={key} className="card" style={{ textAlign: "center", background: style.bg }}>
                  <div style={{ fontSize: 24 }}>{icon}</div>
                  <div style={{ fontSize: 28, fontWeight: 700, color: style.text }}>{results.summary[key]}</div>
                  <div style={{ fontSize: 12, color: style.text }}>{label}</div>
                </div>
              );
            })}
          </div>

          {/* Results list + detail */}
          <div style={{ display: "grid", gridTemplateColumns: selectedResult ? "1fr 1fr" : "1fr", gap: 16 }}>
            {/* Ranked list */}
            <div className="card">
              <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>
                Ranked Candidates ({results.total})
              </h3>
              {results.results.length === 0 ? (
                <p style={{ color: "#9ca3af", fontSize: 13 }}>No results yet. Click "Run Matching" to score resumes.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {results.results.map((r, rank) => {
                    const cat = categoryStyle(r.category);
                    return (
                      <div
                        key={r._id}
                        onClick={() => setSelectedResult(r)}
                        style={{
                          display: "flex", alignItems: "center", gap: 12,
                          padding: "12px 14px", borderRadius: 8, cursor: "pointer",
                          border: selectedResult?._id === r._id ? "1px solid #4f46e5" : "1px solid #e5e7eb",
                          background: selectedResult?._id === r._id ? "#eef2ff" : "#fff",
                        }}
                      >
                        <div style={{
                          width: 28, height: 28, borderRadius: "50%",
                          background: "#f3f4f6", display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: 13, fontWeight: 700, color: "#6b7280", flexShrink: 0,
                        }}>
                          {rank + 1}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 14, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            {r.candidate_name || r.filename}
                          </div>
                          <div style={{ fontSize: 11, color: "#9ca3af" }}>{r.filename}</div>
                        </div>
                        <span style={{
                          fontSize: 11, padding: "3px 10px", borderRadius: 20,
                          background: cat.bg, color: cat.text, fontWeight: 600, flexShrink: 0,
                        }}>
                          {cat.label}
                        </span>
                        <div style={{ fontSize: 18, fontWeight: 700, color: scoreColor(r.overall_score), flexShrink: 0, width: 45, textAlign: "right" }}>
                          {r.overall_score}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Detail breakdown */}
            {selectedResult && (
              <div className="card" style={{ maxHeight: "75vh", overflowY: "auto" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <h3 style={{ fontSize: 15, fontWeight: 600 }}>Score Breakdown</h3>
                  <button onClick={() => setSelectedResult(null)} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 16, color: "#9ca3af" }}>✕</button>
                </div>

                {/* Candidate header */}
                <div style={{ marginBottom: 20, textAlign: "center" }}>
                  <div style={{ fontSize: 18, fontWeight: 700 }}>{selectedResult.candidate_name}</div>
                  <div style={{ fontSize: 36, fontWeight: 700, color: scoreColor(selectedResult.overall_score), marginTop: 4 }}>
                    {selectedResult.overall_score}
                  </div>
                  <span style={{
                    fontSize: 12, padding: "4px 14px", borderRadius: 20, fontWeight: 600,
                    background: categoryStyle(selectedResult.category).bg,
                    color: categoryStyle(selectedResult.category).text,
                  }}>
                    {categoryStyle(selectedResult.category).label}
                  </span>
                </div>

                {/* Explanation */}
                {selectedResult.explanation && (
                  <div style={{ background: "#f9fafb", borderRadius: 8, padding: 14, marginBottom: 16, fontSize: 13, lineHeight: 1.6, color: "#374151" }}>
                    {selectedResult.explanation}
                  </div>
                )}

                {/* Category scores */}
                {selectedResult.score_breakdown && Object.entries(selectedResult.score_breakdown).map(([key, data]) => (
                  <div key={key} style={{ marginBottom: 16 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, textTransform: "capitalize" }}>{key}</span>
                      <span style={{ fontSize: 13, color: "#6b7280" }}>
                        {data.score}/100 × {(data.weight * 100).toFixed(0)}% = <strong>{data.weighted_score}</strong>
                      </span>
                    </div>
                    <div style={{ height: 6, background: "#e5e7eb", borderRadius: 3, overflow: "hidden", marginBottom: 8 }}>
                      <div style={{ height: "100%", width: `${data.score}%`, background: scoreColor(data.score), borderRadius: 3, transition: "width 0.3s" }} />
                    </div>

                    {/* Skills detail */}
                    {key === "skills" && (
                      <div style={{ fontSize: 12, color: "#6b7280" }}>
                        {data.matched?.length > 0 && (
                          <div style={{ marginBottom: 4 }}>
                            <span style={{ color: "#059669" }}>✓ Matched:</span> {data.matched.join(", ")}
                          </div>
                        )}
                        {data.missing?.length > 0 && (
                          <div style={{ marginBottom: 4 }}>
                            <span style={{ color: "#dc2626" }}>✗ Missing:</span> {data.missing.join(", ")}
                          </div>
                        )}
                        {data.preferred_matched?.length > 0 && (
                          <div>
                            <span style={{ color: "#2563eb" }}>★ Preferred:</span> {data.preferred_matched.join(", ")}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Experience detail */}
                    {key === "experience" && (
                      <div style={{ fontSize: 12, color: "#6b7280" }}>
                        {data.candidate_years} years experience (requires {data.required_years})
                        {data.relevant_roles?.length > 0 && (
                          <div style={{ marginTop: 2 }}>Roles: {data.relevant_roles.join(", ")}</div>
                        )}
                      </div>
                    )}

                    {/* Education detail */}
                    {key === "education" && (
                      <div style={{ fontSize: 12, color: "#6b7280" }}>
                        Has: {data.candidate_level} | Requires: {data.required_level}
                        {data.field_match && <span style={{ color: "#059669" }}> (field match ✓)</span>}
                      </div>
                    )}

                    {/* Projects detail */}
                    {key === "projects" && (
                      <div style={{ fontSize: 12, color: "#6b7280" }}>
                        {data.relevant_projects?.length > 0
                          ? `Relevant projects: ${data.relevant_projects.join(", ")}`
                          : "No directly relevant projects"
                        }
                        {data.tech_overlap?.length > 0 && (
                          <div style={{ marginTop: 2 }}>Tech overlap: {data.tech_overlap.join(", ")}</div>
                        )}
                      </div>
                    )}
                  </div>
                ))}

                {/* ML Classification */}
                {selectedResult.ml_predictions && Object.keys(selectedResult.ml_predictions).length > 0 && (
                  <div style={{ marginTop: 8, paddingTop: 16, borderTop: "1px solid #e5e7eb" }}>
                    <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10 }}>ML Category Prediction</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {Object.entries(selectedResult.ml_predictions).map(([model, pred]) => (
                        <div key={model} style={{
                          display: "flex", justifyContent: "space-between", alignItems: "center",
                          padding: "8px 12px", borderRadius: 6, background: "#f9fafb", fontSize: 13,
                        }}>
                          <span style={{ fontWeight: 500 }}>{model}</span>
                          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                            <span style={{ padding: "2px 8px", borderRadius: 12, background: "#eef2ff", color: "#4338ca", fontSize: 11, fontWeight: 600 }}>
                              {pred.category}
                            </span>
                            {pred.confidence && (
                              <span style={{ fontSize: 11, color: "#9ca3af" }}>{pred.confidence}%</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                    <p style={{ fontSize: 11, color: "#9ca3af", marginTop: 8 }}>
                      Predicted job category based on resume content using trained classifiers
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
