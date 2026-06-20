import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { listJobs, listResumes, uploadResumesBulk, deleteResume, getResume } from "../services/api";

export default function Resumes() {
  const [searchParams] = useSearchParams();
  const jobIdFromUrl = searchParams.get("job");

  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(jobIdFromUrl || "");
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState("");
  const fileInputRef = useRef();

  // Fetch jobs on mount
  useEffect(() => {
    listJobs().then(data => setJobs(data.jobs)).catch(() => {});
  }, []);

  // Fetch resumes when job is selected
  useEffect(() => {
    if (selectedJobId) {
      fetchResumes();
    } else {
      setResumes([]);
    }
  }, [selectedJobId]);

  // Auto-select job from URL
  useEffect(() => {
    if (jobIdFromUrl) setSelectedJobId(jobIdFromUrl);
  }, [jobIdFromUrl]);

  const fetchResumes = async () => {
    try {
      const data = await listResumes(selectedJobId);
      setResumes(data.resumes);
    } catch (err) {
      console.error("Failed to fetch resumes:", err);
    }
  };

  const handleFiles = async (files) => {
    if (!selectedJobId) {
      alert("Please select a job first");
      return;
    }
    if (files.length === 0) return;

    setUploading(true);
    setUploadProgress(`Uploading and parsing ${files.length} file(s)...`);

    try {
      const result = await uploadResumesBulk(selectedJobId, Array.from(files));
      setUploadProgress(`Done — ${result.uploaded?.length || 0} parsed successfully, ${result.errors?.length || 0} failed`);
      fetchResumes();
    } catch (err) {
      setUploadProgress("Upload failed: " + err.message);
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(""), 5000);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleDelete = async (resumeId) => {
    if (!window.confirm("Delete this resume?")) return;
    try {
      await deleteResume(resumeId);
      setSelectedResume(null);
      fetchResumes();
    } catch (err) {
      alert("Failed to delete: " + err.message);
    }
  };

  const viewResume = async (resumeId) => {
    try {
      const data = await getResume(resumeId);
      setSelectedResume(data.resume);
    } catch (err) {
      alert("Failed to load resume: " + err.message);
    }
  };

  const statusBadge = (status) => {
    const styles = {
      parsed: "badge-success",
      parsing: "badge-warning",
      uploaded: "badge-warning",
      failed: "badge-danger",
    };
    return <span className={`badge ${styles[status] || ""}`}>{status}</span>;
  };

  return (
    <div>
      <div className="page-header">
        <h2>Resumes</h2>
        <p>Upload and manage candidate CVs</p>
      </div>

      {/* Job selector */}
      <div className="card" style={{ marginBottom: 16 }}>
        <label style={{ fontSize: 13, fontWeight: 500, color: "#374151", display: "block", marginBottom: 6 }}>
          Select a Job Posting
        </label>
        <select
          style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid #d1d5db", fontSize: 14 }}
          value={selectedJobId}
          onChange={e => setSelectedJobId(e.target.value)}
        >
          <option value="">-- Choose a job --</option>
          {jobs.map(job => (
            <option key={job._id} value={job._id}>{job.title} — {job.company}</option>
          ))}
        </select>
      </div>

      {selectedJobId && (
        <>
          {/* Upload zone */}
          <div
            className="card"
            style={{
              marginBottom: 16,
              border: dragActive ? "2px dashed #4f46e5" : "2px dashed #d1d5db",
              background: dragActive ? "#eef2ff" : "#fafafa",
              textAlign: "center",
              padding: 40,
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
            onDragOver={e => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.doc,.docx"
              style={{ display: "none" }}
              onChange={e => handleFiles(e.target.files)}
            />
            <div style={{ fontSize: 32, marginBottom: 8 }}>📄</div>
            <p style={{ fontSize: 15, fontWeight: 500, color: "#374151", marginBottom: 4 }}>
              {uploading ? "Processing..." : "Drop CV files here or click to browse"}
            </p>
            <p style={{ fontSize: 12, color: "#9ca3af" }}>Accepts PDF, DOC, DOCX — multiple files supported</p>
            {uploadProgress && (
              <p style={{ fontSize: 13, color: "#4f46e5", marginTop: 12, fontWeight: 500 }}>{uploadProgress}</p>
            )}
          </div>

          {/* Resume list and detail side by side */}
          <div style={{ display: "grid", gridTemplateColumns: selectedResume ? "1fr 1fr" : "1fr", gap: 16 }}>
            {/* Resume list */}
            <div className="card">
              <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>
                Uploaded CVs ({resumes.length})
              </h3>
              {resumes.length === 0 ? (
                <p style={{ color: "#9ca3af", fontSize: 13 }}>No CVs uploaded yet for this job</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {resumes.map(resume => (
                    <div
                      key={resume._id}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "10px 12px",
                        borderRadius: 8,
                        border: selectedResume?._id === resume._id ? "1px solid #4f46e5" : "1px solid #e5e7eb",
                        background: selectedResume?._id === resume._id ? "#eef2ff" : "#fff",
                        cursor: "pointer",
                      }}
                      onClick={() => viewResume(resume._id)}
                    >
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {resume.filename}
                        </div>
                        <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 2 }}>
                          {resume.parsed_data?.name || "Name not extracted"}
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 8, alignItems: "center", flexShrink: 0 }}>
                        {statusBadge(resume.status)}
                        <button
                          className="btn btn-danger"
                          style={{ fontSize: 11, padding: "4px 10px" }}
                          onClick={e => { e.stopPropagation(); handleDelete(resume._id); }}
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Resume detail */}
            {selectedResume && (
              <div className="card" style={{ maxHeight: "70vh", overflowY: "auto" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <h3 style={{ fontSize: 15, fontWeight: 600 }}>Resume Detail</h3>
                  <button
                    style={{ background: "none", border: "none", cursor: "pointer", fontSize: 16, color: "#9ca3af" }}
                    onClick={() => setSelectedResume(null)}
                  >
                    ✕
                  </button>
                </div>

                {/* Contact info */}
                <Section title="Contact">
                  <Field label="Name" value={selectedResume.parsed_data?.name} />
                  <Field label="Email" value={selectedResume.parsed_data?.email} />
                  <Field label="Phone" value={selectedResume.parsed_data?.phone} />
                  <Field label="Location" value={selectedResume.parsed_data?.location} />
                </Section>

                {/* Summary */}
                {selectedResume.parsed_data?.summary && (
                  <Section title="Summary">
                    <p style={{ fontSize: 13, color: "#374151", lineHeight: 1.6 }}>{selectedResume.parsed_data.summary}</p>
                  </Section>
                )}

                {/* Skills */}
                <Section title="Skills">
                  {selectedResume.parsed_data?.skills?.length > 0 ? (
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      {selectedResume.parsed_data.skills.map((skill, i) => (
                        <span key={i} style={{ fontSize: 12, padding: "3px 10px", borderRadius: 12, background: "#eef2ff", color: "#4338ca" }}>{skill}</span>
                      ))}
                    </div>
                  ) : <Empty />}
                </Section>

                {/* Experience */}
                <Section title="Experience">
                  {selectedResume.parsed_data?.experience?.length > 0 ? (
                    selectedResume.parsed_data.experience.map((exp, i) => (
                      <div key={i} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #f3f4f6" }}>
                        <div style={{ fontSize: 13, fontWeight: 600 }}>{exp.job_title || "Untitled Role"}</div>
                        <div style={{ fontSize: 12, color: "#6b7280" }}>{exp.company}</div>
                        <div style={{ fontSize: 11, color: "#9ca3af" }}>{exp.start_date} — {exp.end_date}</div>
                        {exp.description && <p style={{ fontSize: 12, color: "#374151", marginTop: 4, lineHeight: 1.5 }}>{exp.description}</p>}
                      </div>
                    ))
                  ) : <Empty />}
                </Section>

                {/* Education */}
                <Section title="Education">
                  {selectedResume.parsed_data?.education?.length > 0 ? (
                    selectedResume.parsed_data.education.map((edu, i) => (
                      <div key={i} style={{ marginBottom: 8 }}>
                        <div style={{ fontSize: 13, fontWeight: 600 }}>{edu.degree}{edu.field ? ` in ${edu.field}` : ""}</div>
                        <div style={{ fontSize: 12, color: "#6b7280" }}>{edu.institution}</div>
                        {edu.year && <div style={{ fontSize: 11, color: "#9ca3af" }}>{edu.year}</div>}
                      </div>
                    ))
                  ) : <Empty />}
                </Section>

                {/* Projects */}
                <Section title="Projects">
                  {selectedResume.parsed_data?.projects?.length > 0 ? (
                    selectedResume.parsed_data.projects.map((proj, i) => (
                      <div key={i} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #f3f4f6" }}>
                        <div style={{ fontSize: 13, fontWeight: 600 }}>{proj.title}</div>
                        {proj.technologies?.length > 0 && (
                          <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 4 }}>
                            {proj.technologies.map((tech, j) => (
                              <span key={j} style={{ fontSize: 10, padding: "2px 6px", borderRadius: 8, background: "#ecfdf5", color: "#047857" }}>{tech}</span>
                            ))}
                          </div>
                        )}
                        {proj.description && <p style={{ fontSize: 12, color: "#374151", marginTop: 4, lineHeight: 1.5 }}>{proj.description}</p>}
                      </div>
                    ))
                  ) : <Empty />}
                </Section>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <h4 style={{ fontSize: 12, fontWeight: 600, color: "#6b7280", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 8 }}>{title}</h4>
      {children}
    </div>
  );
}

function Field({ label, value }) {
  return (
    <div style={{ display: "flex", fontSize: 13, marginBottom: 4 }}>
      <span style={{ color: "#6b7280", width: 70, flexShrink: 0 }}>{label}</span>
      <span style={{ color: value ? "#374151" : "#d1d5db" }}>{value || "—"}</span>
    </div>
  );
}

function Empty() {
  return <p style={{ fontSize: 12, color: "#d1d5db" }}>Not detected</p>;
}
