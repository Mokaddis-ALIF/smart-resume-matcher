import { useState, useEffect } from "react";
import { checkHealth, listJobs } from "../services/api";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    checkHealth().then(setHealth).catch(() => setHealth({ status: "error", database: "error" }));
    listJobs().then((data) => setJobs(data.jobs)).catch(() => {});
  }, []);

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>System overview and status</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 24 }}>
        <div className="card">
          <div style={{ fontSize: 13, color: "#6b7280", marginBottom: 6 }}>API Status</div>
          <div style={{ fontSize: 20, fontWeight: 700 }}>
            {health ? (health.status === "running" ? "🟢 Running" : "🔴 Down") : "⏳ Checking..."}
          </div>
        </div>
        <div className="card">
          <div style={{ fontSize: 13, color: "#6b7280", marginBottom: 6 }}>Database</div>
          <div style={{ fontSize: 20, fontWeight: 700 }}>
            {health ? (health.database === "connected" ? "🟢 Connected" : "🔴 Disconnected") : "⏳ Checking..."}
          </div>
        </div>
        <div className="card">
          <div style={{ fontSize: 13, color: "#6b7280", marginBottom: 6 }}>Active Jobs</div>
          <div style={{ fontSize: 20, fontWeight: 700 }}>{jobs.length}</div>
        </div>
      </div>
    </div>
  );
}
