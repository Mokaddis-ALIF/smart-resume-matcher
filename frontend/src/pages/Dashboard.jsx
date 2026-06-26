import { useState, useEffect } from "react";
import { checkHealth, listJobs, getEvaluationResults } from "../services/api";

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
        setJobs(data.jobs);
        const total = data.jobs.reduce((sum, j) => sum + (j.matched_count || 0), 0);
        setTotalResumes(total);
      })
      .catch(() => { });

    getEvaluationResults()
      .then(setEvalData)
      .catch(() => { });
  }, []);

  const bestModel = evalData?.results
    ? Object.entries(evalData.results).reduce((a, b) => a[1].f1_score > b[1].f1_score ? a : b)
    : null;

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Smart Resume Matching Tool — System Overview</p>
      </div>

      {/* System status */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
        <StatusCard
          label="API Status"
          value={health ? (health.status === "running" ? "🟢 Running" : "🔴 Down") : "⏳ Checking..."}
        />
        <StatusCard
          label="Database"
          value={health ? (health.database === "connected" ? "🟢 Connected" : "🔴 Disconnected") : "⏳ Checking..."}
        />
        <StatusCard label="Active Jobs" value={jobs.length} />
        <StatusCard label="Resumes Processed" value={totalResumes} />
      </div>

      {/* Quick actions */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 14 }}>Quick Start</h3>
        <div style={{ display: "flex", gap: 12 }}>
          <a href="/jobs" className="btn btn-primary" style={{ textDecoration: "none" }}>Create a Job Posting</a>
          <a href="/resumes" style={{ textDecoration: "none", padding: "9px 18px", borderRadius: 8, fontSize: 14, fontWeight: 500, border: "1px solid #d1d5db", color: "#374151", background: "#fff" }}>Upload CVs</a>
          <a href="/results" style={{ textDecoration: "none", padding: "9px 18px", borderRadius: 8, fontSize: 14, fontWeight: 500, border: "1px solid #d1d5db", color: "#374151", background: "#fff" }}>View Results</a>
          <a href="/evaluation" style={{ textDecoration: "none", padding: "9px 18px", borderRadius: 8, fontSize: 14, fontWeight: 500, border: "1px solid #d1d5db", color: "#374151", background: "#fff" }}>Model Evaluation</a>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Recent jobs */}
        <div className="card">
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>Recent Job Postings</h3>
          {jobs.length === 0 ? (
            <p style={{ fontSize: 13, color: "#9ca3af" }}>No jobs created yet</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {jobs.slice(0, 5).map(job => (
                <div key={job._id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid #f3f4f6" }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>{job.title}</div>
                  </div>
                  <span style={{ fontSize: 12, color: "#6b7280" }}>{job.matched_count || 0} matched</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ML model summary */}
        <div className="card">
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>ML Model Performance</h3>
          {!evalData ? (
            <p style={{ fontSize: 13, color: "#9ca3af" }}>Models not trained yet — go to Evaluation page</p>
          ) : (
            <div>
              {bestModel && (
                <div style={{ padding: "8px 12px", borderRadius: 8, background: "#f0fdf4", marginBottom: 12, fontSize: 13 }}>
                  <span style={{ fontWeight: 600, color: "#059669" }}>🏆 Best: {bestModel[0]}</span>
                  <span style={{ color: "#6b7280" }}> — {bestModel[1].f1_score}% F1 Score</span>
                </div>
              )}
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {Object?.entries(evalData?.dataset1?.results).map(([name, metrics]) => (
                  <div key={name} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 12, width: 100, color: "#6b7280" }}>{name}</span>
                    <div style={{ flex: 1, height: 14, background: "#f3f4f6", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${metrics.f1_score}%`, background: name === bestModel?.[0] ? "#059669" : "#94a3b8", borderRadius: 3 }} />
                    </div>
                    <span style={{ fontSize: 12, fontWeight: 500, width: 45, textAlign: "right" }}>{metrics.f1_score}%</span>
                  </div>
                ))}
              </div>
              <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 8 }}>
                Trained on {evalData.dataset_size} resumes across {evalData.categories?.length} categories
              </div>
            </div>
          )}
        </div>
      </div>

      {/* System info */}
      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>System Architecture</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, fontSize: 13 }}>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 6, color: "#4f46e5" }}>Backend</div>
            <div style={{ color: "#6b7280", lineHeight: 1.8 }}>
              Python, Flask<br />MongoDB (PyMongo)<br />PyMuPDF, python-docx
            </div>
          </div>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 6, color: "#059669" }}>NLP / ML</div>
            <div style={{ color: "#6b7280", lineHeight: 1.8 }}>
              spaCy (NER)<br />BERT (Sentence Transformers)<br />scikit-learn (SVM, RF, KNN, NB)
            </div>
          </div>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 6, color: "#d97706" }}>Frontend</div>
            <div style={{ color: "#6b7280", lineHeight: 1.8 }}>
              React (Vite)<br />React Router<br />REST API integration
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusCard({ label, value }) {
  return (
    <div className="card">
      <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 700 }}>{value}</div>
    </div>
  );
}
