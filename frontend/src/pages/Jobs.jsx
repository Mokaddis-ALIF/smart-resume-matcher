import { useState, useEffect, useCallback } from "react";
import { listJobs, createJob, updateJob, deleteJob, getSoftSkills, addSoftSkill, validateSkills } from "../services/api";

const emptyForm = {
  title: "",
  description: "",
  required_skills: "",
  preferred_skills: "",
  min_experience_years: 0,
  education_level: "none",
  soft_skills: [],
};

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingJobId, setEditingJobId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ ...emptyForm });
  const [softSkillOptions, setSoftSkillOptions] = useState([]);
  const [newSoftSkill, setNewSoftSkill] = useState("");
  const [showSoftSkillInput, setShowSoftSkillInput] = useState(false);
  const [reqValidation, setReqValidation] = useState([]);
  const [prefValidation, setPrefValidation] = useState([]);

  const fetchJobs = async () => {
    try {
      const data = await listJobs();
      setJobs(data.jobs);
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSoftSkills = async () => {
    try {
      const data = await getSoftSkills();
      setSoftSkillOptions(data.soft_skills);
    } catch (err) {
      console.error("Failed to fetch soft skills:", err);
    }
  };

  useEffect(() => { fetchJobs(); fetchSoftSkills(); }, []);

  // Debounced skill validation
  const validateField = useCallback((text, setter) => {
    const skills = text.split(",").map(s => s.trim()).filter(Boolean);
    if (skills.length === 0) { setter([]); return; }

    const timer = setTimeout(async () => {
      try {
        const data = await validateSkills(skills);
        setter(data.results);
      } catch { setter([]); }
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const cleanup = validateField(form.required_skills, setReqValidation);
    return cleanup;
  }, [form.required_skills, validateField]);

  useEffect(() => {
    const cleanup = validateField(form.preferred_skills, setPrefValidation);
    return cleanup;
  }, [form.preferred_skills, validateField]);

  const openCreateForm = () => {
    setEditingJobId(null);
    setForm({ ...emptyForm });
    setReqValidation([]);
    setPrefValidation([]);
    setShowForm(true);
  };

  const openEditForm = (job) => {
    setEditingJobId(job._id);
    setForm({
      title: job.title || "",
      description: job.description || "",
      required_skills: (job.requirements?.required_skills || []).join(", "),
      preferred_skills: (job.requirements?.preferred_skills || []).join(", "),
      min_experience_years: job.requirements?.min_experience_years || 0,
      education_level: job.requirements?.education_level || "none",
      soft_skills: job.soft_skills || [],
    });
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingJobId(null);
    setForm({ ...emptyForm });
    setReqValidation([]);
    setPrefValidation([]);
  };

  const buildJobData = () => ({
    title: form.title,
    description: form.description,
    requirements: {
      required_skills: form.required_skills.split(",").map(s => s.trim()).filter(Boolean),
      preferred_skills: form.preferred_skills.split(",").map(s => s.trim()).filter(Boolean),
      min_experience_years: parseInt(form.min_experience_years) || 0,
      education_level: form.education_level,
    },
    soft_skills: form.soft_skills,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingJobId) {
        await updateJob(editingJobId, buildJobData());
        alert("Job updated. All previous resumes and match results have been cleared. Upload new CVs and run matching again.");
      } else {
        const result = await createJob(buildJobData());
        if (result.duplicate_warning) {
          alert(result.duplicate_warning);
        }
      }
      closeForm();
      fetchJobs();
    } catch (err) {
      alert("Failed to save job: " + err.message);
    }
  };

  const handleAddSoftSkill = async () => {
    if (!newSoftSkill.trim()) return;
    try {
      await addSoftSkill(newSoftSkill.trim());
      await fetchSoftSkills();
      setForm({ ...form, soft_skills: [...form.soft_skills, newSoftSkill.trim()] });
      setNewSoftSkill("");
      setShowSoftSkillInput(false);
    } catch (err) {
      alert(err.message);
    }
  };

  const toggleSoftSkill = (skill) => {
    const current = form.soft_skills;
    if (current.includes(skill)) {
      setForm({ ...form, soft_skills: current.filter(s => s !== skill) });
    } else {
      setForm({ ...form, soft_skills: [...current, skill] });
    }
  };

  const handleDelete = async (jobId) => {
    if (!window.confirm("Delete this job and all its resumes and match results?")) return;
    try {
      await deleteJob(jobId);
      fetchJobs();
    } catch (err) {
      alert("Failed to delete: " + err.message);
    }
  };

  const renderSkillTags = (validation) => {
    if (!validation.length) return null;
    return (
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 6 }}>
        {validation.map((v, i) => (
          <span key={i} style={{
            fontSize: 11, padding: "3px 10px", borderRadius: 12,
            display: "flex", alignItems: "center", gap: 4,
            background: v.matched ? (v.fuzzy ? "#fef3c7" : "#d1fae5") : "#fee2e2",
            color: v.matched ? (v.fuzzy ? "#92400e" : "#059669") : "#dc2626",
            border: v.matched ? (v.fuzzy ? "1px solid #fcd34d" : "1px solid #a7f3d0") : "1px solid #fecaca",
          }}>
            {v.matched ? "✓" : "✗"} {v.canonical || v.input}
            {v.matched && v.canonical !== v.input && (
              <span style={{ fontSize: 9, opacity: 0.7 }}>← {v.input}</span>
            )}
          </span>
        ))}
      </div>
    );
  };

  const unmatchedCount = (validation) => validation.filter(v => !v.matched).length;

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2>Job Postings</h2>
          <p>Create job postings and upload CVs against them</p>
        </div>
        <button className="btn btn-primary" onClick={showForm ? closeForm : openCreateForm}>
          {showForm ? "Cancel" : "+ New Job"}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>
            {editingJobId ? "Edit Job Posting" : "Create New Job Posting"}
          </h3>
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={labelStyle}>Job Title *</label>
              <input style={inputStyle} required value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="e.g. Senior Python Developer" />
            </div>
            <div>
              <label style={labelStyle}>Job Description *</label>
              <textarea style={{...inputStyle, minHeight: 80, resize: "vertical"}} required value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Describe the role, responsibilities, and what you're looking for..." />
            </div>
            <div>
              <label style={labelStyle}>Required Technical Skills (comma separated) *</label>
              <input style={inputStyle} required value={form.required_skills} onChange={e => setForm({...form, required_skills: e.target.value})} placeholder="e.g. Python, Flask, MongoDB, Docker" />
              {renderSkillTags(reqValidation)}
              {unmatchedCount(reqValidation) > 0 && (
                <div style={{ fontSize: 11, color: "#92400e", marginTop: 4 }}>
                  ⚠ {unmatchedCount(reqValidation)} skill(s) not in taxonomy — these won't match against CVs. Consider removing or rephrasing.
                </div>
              )}
            </div>
            <div>
              <label style={labelStyle}>Preferred Technical Skills (comma separated)</label>
              <input style={inputStyle} value={form.preferred_skills} onChange={e => setForm({...form, preferred_skills: e.target.value})} placeholder="e.g. Kubernetes, AWS, Redis" />
              {renderSkillTags(prefValidation)}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
              <div>
                <label style={labelStyle}>Min. Experience (years)</label>
                <input style={inputStyle} type="number" min="0" value={form.min_experience_years} onChange={e => setForm({...form, min_experience_years: e.target.value})} />
              </div>
              <div>
                <label style={labelStyle}>Education Requirement</label>
                <select style={inputStyle} value={form.education_level} onChange={e => setForm({...form, education_level: e.target.value})}>
                  <option value="none">None Required</option>
                  <option value="bachelors">Bachelor's (IT-related field)</option>
                  <option value="masters">Master's (IT-related field)</option>
                  <option value="phd">PhD (IT-related field)</option>
                </select>
              </div>
            </div>
            {form.education_level !== "none" && (
              <div style={{
                fontSize: 11, color: "#6b7280", padding: "8px 12px",
                background: "#f9fafb", borderRadius: 6, lineHeight: 1.6,
              }}>
                <strong>IT-related fields that qualify:</strong> Computer Science, Software Engineering, Data Science,
                Information Technology, Computer Engineering, Mathematics, Statistics, Electronics,
                Artificial Intelligence, Cybersecurity, and similar tech fields.
                Non-IT degrees (Finance, Arts, Business, etc.) will not satisfy this requirement.
              </div>
            )}

            {/* Soft Skills */}
            <div>
              <label style={labelStyle}>Soft Skills (optional — not scored, for interview reference)</label>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
                {softSkillOptions.map(skill => (
                  <button
                    key={skill}
                    type="button"
                    onClick={() => toggleSoftSkill(skill)}
                    style={{
                      fontSize: 12, padding: "4px 12px", borderRadius: 20, cursor: "pointer",
                      border: form.soft_skills.includes(skill) ? "2px solid #4f46e5" : "1px solid #d1d5db",
                      background: form.soft_skills.includes(skill) ? "#eef2ff" : "#fff",
                      color: form.soft_skills.includes(skill) ? "#4f46e5" : "#6b7280",
                      fontWeight: form.soft_skills.includes(skill) ? 600 : 400,
                    }}
                  >
                    {form.soft_skills.includes(skill) ? "✓ " : ""}{skill}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={() => setShowSoftSkillInput(!showSoftSkillInput)}
                  style={{
                    fontSize: 12, padding: "4px 12px", borderRadius: 20, cursor: "pointer",
                    border: "1px dashed #9ca3af", background: "#f9fafb", color: "#6b7280",
                  }}
                >
                  + Add New
                </button>
              </div>
              {showSoftSkillInput && (
                <div style={{ display: "flex", gap: 8 }}>
                  <input
                    style={{ ...inputStyle, flex: 1 }}
                    value={newSoftSkill}
                    onChange={e => setNewSoftSkill(e.target.value)}
                    placeholder="Type a new soft skill..."
                    onKeyDown={e => e.key === "Enter" && (e.preventDefault(), handleAddSoftSkill())}
                  />
                  <button type="button" onClick={handleAddSoftSkill} className="btn btn-primary" style={{ fontSize: 13 }}>Add</button>
                </div>
              )}
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <button className="btn btn-primary" type="submit">
                {editingJobId ? "Save Changes" : "Create Job"}
              </button>
              {editingJobId && (
                <button type="button" onClick={closeForm} style={{
                  padding: "9px 18px", borderRadius: 8, fontSize: 14, fontWeight: 500,
                  border: "1px solid #d1d5db", background: "#fff", color: "#374151", cursor: "pointer",
                }}>
                  Cancel Edit
                </button>
              )}
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <p style={{ color: "#6b7280" }}>Loading jobs...</p>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: 40, color: "#6b7280" }}>
          <p style={{ fontSize: 16, marginBottom: 4 }}>No job postings yet</p>
          <p style={{ fontSize: 13 }}>Click "+ New Job" to create your first posting</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {jobs.map(job => (
            <div key={job._id} className="card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
                    {job.reference && (
                      <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 4, background: "#f3f4f6", color: "#6b7280", fontWeight: 600, fontFamily: "monospace" }}>
                        {job.reference}
                      </span>
                    )}
                    <h3 style={{ fontSize: 15, fontWeight: 600 }}>{job.title}</h3>
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {job.requirements?.required_skills?.map((skill, i) => (
                      <span key={i} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 12, background: "#eef2ff", color: "#4338ca" }}>{skill}</span>
                    ))}
                    {job.requirements?.preferred_skills?.map((skill, i) => (
                      <span key={`p${i}`} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 12, background: "#f0fdf4", color: "#059669" }}>{skill}</span>
                    ))}
                  </div>
                  {job.soft_skills?.length > 0 && (
                    <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 6 }}>
                      {job.soft_skills.map((skill, i) => (
                        <span key={i} style={{ fontSize: 10, padding: "2px 7px", borderRadius: 12, background: "#f3f4f6", color: "#6b7280" }}>{skill}</span>
                      ))}
                    </div>
                  )}
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center", flexShrink: 0 }}>
                  <a href={`/resumes?job=${job._id}`} className="btn btn-primary" style={{ textDecoration: "none", fontSize: 13 }}>Upload CVs</a>
                  <button onClick={() => openEditForm(job)} style={{
                    padding: "7px 14px", borderRadius: 8, fontSize: 13, fontWeight: 500,
                    border: "1px solid #d1d5db", background: "#fff", color: "#374151", cursor: "pointer",
                  }}>✏️ Edit</button>
                  <button className="btn btn-danger" style={{ fontSize: 13 }} onClick={() => handleDelete(job._id)}>Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const labelStyle = { display: "block", fontSize: 13, fontWeight: 500, color: "#374151", marginBottom: 4 };
const inputStyle = { width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid #d1d5db", fontSize: 14, fontFamily: "inherit", outline: "none" };
