import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { listJobs, listResumes, uploadResumesBulk, deleteResume, deleteResumesBulk, getResume } from "../services/api";

export default function Resumes() {
  const [searchParams] = useSearchParams();
  const jobIdFromUrl = searchParams.get("job");

  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(jobIdFromUrl || "");
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState(null);
  const [viewingPdf, setViewingPdf] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
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
      setSelectedIds(prev => { const n = new Set(prev); n.delete(resumeId); return n; });
      fetchResumes();
    } catch (err) {
      alert("Failed to delete: " + err.message);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!window.confirm(`Delete ${selectedIds.size} selected resume(s)?`)) return;
    try {
      await deleteResumesBulk(Array.from(selectedIds));
      setSelectedIds(new Set());
      setSelectedResume(null);
      fetchResumes();
    } catch (err) {
      alert("Failed to delete: " + err.message);
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === resumes.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(resumes.map(r => r._id)));
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
            <option key={job._id} value={job._id}>{job.title}</option>
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
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <h3 style={{ fontSize: 15, fontWeight: 600 }}>
                  Uploaded CVs ({resumes.length})
                </h3>
                {resumes.length > 0 && (
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <label style={{ fontSize: 12, color: "#6b7280", cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}>
                      <input
                        type="checkbox"
                        checked={selectedIds.size === resumes.length && resumes.length > 0}
                        onChange={toggleSelectAll}
                        style={{ accentColor: "#4f46e5", cursor: "pointer" }}
                      />
                      Select All
                    </label>
                    {selectedIds.size > 0 && (
                      <button
                        className="btn btn-danger"
                        style={{ fontSize: 11, padding: "4px 12px" }}
                        onClick={handleBulkDelete}
                      >
                        Delete {selectedIds.size} Selected
                      </button>
                    )}
                  </div>
                )}
              </div>
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
                      <div style={{ display: "flex", alignItems: "flex-start", gap: 8, minWidth: 0 }}>
                        <input
                          type="checkbox"
                          checked={selectedIds.has(resume._id)}
                          onChange={() => toggleSelect(resume._id)}
                          onClick={e => e.stopPropagation()}
                          style={{ marginTop: 3, accentColor: "#4f46e5", cursor: "pointer", flexShrink: 0 }}
                        />
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {resume.filename}
                        </div>
                        <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 2 }}>
                          {resume.parsed_data?.name || "Name not extracted"}
                        </div>
                        {resume.status === "failed" && resume.error_message && (
                          <div style={{
                            fontSize: 11, color: "#dc2626", marginTop: 4,
                            padding: "4px 8px", borderRadius: 4,
                            background: "#fef2f2", lineHeight: 1.4,
                          }}>
                            ⚠ {resume.error_message}
                          </div>
                        )}
                      </div>
                      </div>
                      <div style={{ display: "flex", gap: 6, alignItems: "center", flexShrink: 0 }}>
                        {statusBadge(resume.status)}
                        <button
                          style={{
                            fontSize: 11, padding: "4px 10px", borderRadius: 6,
                            border: "1px solid #c7d2fe", background: "#eef2ff",
                            color: "#4338ca", cursor: "pointer", fontWeight: 500,
                          }}
                          onClick={e => { e.stopPropagation(); setViewingPdf(resume); }}
                        >
                          👁 View
                        </button>
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

                {/* Skills — NLP Enhanced */}
                <Section title="Skills (NLP Extracted)">
                  {selectedResume.nlp_data?.extracted_skills?.length > 0 ? (
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      {selectedResume.nlp_data.extracted_skills.map((s, i) => {
                        const catColors = {
                          language: { bg: "#eef2ff", text: "#4338ca" },
                          framework: { bg: "#f0fdf4", text: "#166534" },
                          database: { bg: "#fef3c7", text: "#92400e" },
                          cloud: { bg: "#eff6ff", text: "#1e40af" },
                          devops: { bg: "#fce7f3", text: "#9d174d" },
                          tool: { bg: "#f3f4f6", text: "#374151" },
                          ml: { bg: "#faf5ff", text: "#7c3aed" },
                          mobile: { bg: "#ecfdf5", text: "#047857" },
                          testing: { bg: "#fff7ed", text: "#c2410c" },
                          methodology: { bg: "#f0f9ff", text: "#0369a1" },
                          messaging: { bg: "#fdf2f8", text: "#be185d" },
                          unknown: { bg: "#f9fafb", text: "#6b7280" },
                        };
                        const colors = catColors[s.category] || catColors.unknown;
                        return (
                          <span key={i} style={{
                            fontSize: 11, padding: "4px 10px", borderRadius: 12,
                            background: colors.bg, color: colors.text,
                            display: "flex", alignItems: "center", gap: 4,
                          }}>
                            {s.skill}
                            <span style={{ fontSize: 9, opacity: 0.7 }}>{Math.round(s.confidence * 100)}%</span>
                          </span>
                        );
                      })}
                    </div>
                  ) : (
                    /* Fallback to parsed skills if NLP hasn't run */
                    selectedResume.parsed_data?.skills?.length > 0 ? (
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {selectedResume.parsed_data.skills.map((skill, i) => (
                          <span key={i} style={{ fontSize: 12, padding: "3px 10px", borderRadius: 12, background: "#eef2ff", color: "#4338ca" }}>{skill}</span>
                        ))}
                      </div>
                    ) : <Empty />
                  )}
                </Section>

                {/* Named Entities — spaCy NER */}
                {selectedResume.nlp_data?.entities?.length > 0 && (
                  <Section title="Named Entities (spaCy NER)">
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      {selectedResume.nlp_data.entities.map((ent, i) => {
                        const labelColors = {
                          PERSON: { bg: "#dbeafe", text: "#1e40af" },
                          ORG: { bg: "#dcfce7", text: "#166534" },
                          GPE: { bg: "#fef9c3", text: "#854d0e" },
                          DATE: { bg: "#f3e8ff", text: "#7c3aed" },
                          PRODUCT: { bg: "#ffe4e6", text: "#be123c" },
                        };
                        const colors = labelColors[ent.label] || { bg: "#f3f4f6", text: "#6b7280" };
                        return (
                          <span key={i} style={{
                            fontSize: 11, padding: "3px 8px", borderRadius: 6,
                            background: colors.bg, color: colors.text,
                            display: "flex", alignItems: "center", gap: 4,
                          }}>
                            <span style={{ fontSize: 9, fontWeight: 700, opacity: 0.6 }}>{ent.label}</span>
                            {ent.text}
                          </span>
                        );
                      })}
                    </div>
                  </Section>
                )}

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

      {/* PDF Viewer Modal */}
      {viewingPdf && (
        <div
          style={{
            position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
            background: "rgba(0, 0, 0, 0.6)", zIndex: 1000,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
          onClick={() => setViewingPdf(null)}
        >
          <div
            style={{
              background: "#fff", borderRadius: 12, width: "80%", height: "90vh",
              display: "flex", flexDirection: "column", overflow: "hidden",
            }}
            onClick={e => e.stopPropagation()}
          >
            {/* Modal header */}
            <div style={{
              display: "flex", justifyContent: "space-between", alignItems: "center",
              padding: "14px 20px", borderBottom: "1px solid #e5e7eb",
            }}>
              <div>
                <div style={{ fontSize: 15, fontWeight: 600 }}>{viewingPdf.filename}</div>
                <div style={{ fontSize: 12, color: "#9ca3af" }}>
                  {viewingPdf.parsed_data?.name || "Unknown candidate"}
                </div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <a
                  href={`http://localhost:5000/api/resumes/${viewingPdf._id}/file`}
                  download={viewingPdf.filename}
                  style={{
                    fontSize: 12, padding: "6px 14px", borderRadius: 6,
                    border: "1px solid #d1d5db", background: "#fff",
                    color: "#374151", textDecoration: "none", fontWeight: 500,
                  }}
                >
                  ⬇ Download
                </a>
                <button
                  onClick={() => setViewingPdf(null)}
                  style={{
                    fontSize: 16, padding: "4px 12px", borderRadius: 6,
                    border: "1px solid #d1d5db", background: "#fff",
                    color: "#6b7280", cursor: "pointer",
                  }}
                >
                  ✕
                </button>
              </div>
            </div>

            {/* PDF embed */}
            <div style={{ flex: 1, background: "#525659" }}>
              {viewingPdf.file_format === "pdf" ? (
                <iframe
                  src={`http://localhost:5000/api/resumes/${viewingPdf._id}/file`}
                  style={{ width: "100%", height: "100%", border: "none" }}
                  title="Resume PDF"
                />
              ) : (
                <div style={{
                  display: "flex", alignItems: "center", justifyContent: "center",
                  height: "100%", color: "#fff", flexDirection: "column", gap: 12,
                }}>
                  <div style={{ fontSize: 48 }}>📄</div>
                  <p style={{ fontSize: 14 }}>Preview not available for {viewingPdf.file_format?.toUpperCase()} files</p>
                  <a
                    href={`http://localhost:5000/api/resumes/${viewingPdf._id}/file`}
                    download={viewingPdf.filename}
                    style={{
                      padding: "8px 20px", borderRadius: 8, background: "#4f46e5",
                      color: "#fff", textDecoration: "none", fontSize: 14, fontWeight: 500,
                    }}
                  >
                    Download to view
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
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
