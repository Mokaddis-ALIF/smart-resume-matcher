import { useState, useEffect } from "react";
import { listJobs, createJob, updateJob, deleteJob } from "../services/api";

const emptyForm = {
  title: "",
  description: "",
  required_skills: "",
  preferred_skills: "",
  min_experience_years: 0,
  education_level: "bachelors",
  education_field: "",
};

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingJobId, setEditingJobId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ ...emptyForm });

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

  useEffect(() => { fetchJobs(); }, []);

  const openCreateForm = () => {
    setEditingJobId(null);
    setForm({ ...emptyForm });
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
      education_level: job.requirements?.education_level || "bachelors",
      education_field: job.requirements?.education_field || "",
    });
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingJobId(null);
    setForm({ ...emptyForm });
  };

  const buildJobData = () => ({
    title: form.title,
    description: form.description,
    requirements: {
      required_skills: form.required_skills.split(",").map(s => s.trim()).filter(Boolean),
      preferred_skills: form.preferred_skills.split(",").map(s => s.trim()).filter(Boolean),
      min_experience_years: parseInt(form.min_experience_years) || 0,
      education_level: form.education_level,
      education_field: form.education_field,
    },
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingJobId) {
        await updateJob(editingJobId, buildJobData());
        alert("Job updated. All previous resumes and match results have been cleared. Upload new CVs and run matching again.");
      } else {
        await createJob(buildJobData());
      }
      closeForm();
      fetchJobs();
    } catch (err) {
      alert("Failed to save job: " + err.message);
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
              <label style={labelStyle}>Required Skills (comma separated) *</label>
              <input style={inputStyle} required value={form.required_skills} onChange={e => setForm({...form, required_skills: e.target.value})} placeholder="e.g. Python, Flask, MongoDB, Docker" />
            </div>
            <div>
              <label style={labelStyle}>Preferred Skills (comma separated)</label>
              <input style={inputStyle} value={form.preferred_skills} onChange={e => setForm({...form, preferred_skills: e.target.value})} placeholder="e.g. Kubernetes, AWS, Redis" />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
              <div>
                <label style={labelStyle}>Min. Experience (years)</label>
                <input style={inputStyle} type="number" min="0" value={form.min_experience_years} onChange={e => setForm({...form, min_experience_years: e.target.value})} />
              </div>
              <div>
                <label style={labelStyle}>Education Level</label>
                <select style={inputStyle} value={form.education_level} onChange={e => setForm({...form, education_level: e.target.value})}>
                  <option value="none">None Required</option>
                  <option value="diploma">Diploma</option>
                  <option value="bachelors">Bachelor's</option>
                  <option value="masters">Master's</option>
                  <option value="phd">PhD</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Education Field</label>
                <input style={inputStyle} value={form.education_field} onChange={e => setForm({...form, education_field: e.target.value})} placeholder="e.g. Computer Science" />
              </div>
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
            <div key={job._id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 3 }}>{job.title}</h3>
                <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap" }}>
                  {job.requirements?.required_skills?.map((skill, i) => (
                    <span key={i} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 12, background: "#eef2ff", color: "#4338ca" }}>{skill}</span>
                  ))}
                </div>
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <a href={`/resumes?job=${job._id}`} className="btn btn-primary" style={{ textDecoration: "none", fontSize: 13 }}>Upload CVs</a>
                <button
                  onClick={() => openEditForm(job)}
                  style={{
                    padding: "7px 14px", borderRadius: 8, fontSize: 13, fontWeight: 500,
                    border: "1px solid #d1d5db", background: "#fff", color: "#374151", cursor: "pointer",
                  }}
                >
                  ✏️ Edit
                </button>
                <button className="btn btn-danger" style={{ fontSize: 13 }} onClick={() => handleDelete(job._id)}>Delete</button>
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
