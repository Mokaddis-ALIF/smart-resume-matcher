/**
 * API service — centralised functions for calling the backend.
 * Base URL points to Flask dev server.
 */

const BASE_URL = "http://localhost:5000/api";

/**
 * Generic fetch wrapper with error handling.
 */
async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

// ─── Health ───

export function checkHealth() {
  return request("/health");
}

// ─── Jobs ───

export function createJob(jobData) {
  return request("/jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(jobData),
  });
}

export function listJobs() {
  return request("/jobs");
}

export function getJob(jobId) {
  return request(`/jobs/${jobId}`);
}

export function updateJob(jobId, updates) {
  return request(`/jobs/${jobId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
}

export function deleteJob(jobId) {
  return request(`/jobs/${jobId}`, { method: "DELETE" });
}

export function getSoftSkills() {
  return request("/soft-skills");
}

export function addSoftSkill(name) {
  return request("/soft-skills", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export function validateSkills(skills) {
  return request("/skills/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ skills }),
  });
}

export function triggerMatching(jobId) {
  return request(`/jobs/${jobId}/match`, { method: "POST" });
}

export function getResults(jobId) {
  return request(`/jobs/${jobId}/results`);
}

// ─── Resumes ───

export function uploadResume(jobId, file) {
  const formData = new FormData();
  formData.append("file", file);
  return request(`/jobs/${jobId}/resumes/upload`, {
    method: "POST",
    body: formData,
  });
}

export function uploadResumesBulk(jobId, files) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  return request(`/jobs/${jobId}/resumes/upload/bulk`, {
    method: "POST",
    body: formData,
  });
}

export function listResumes(jobId) {
  return request(`/jobs/${jobId}/resumes`);
}

export function getResume(resumeId) {
  return request(`/resumes/${resumeId}`);
}

export function deleteResume(resumeId) {
  return request(`/resumes/${resumeId}`, { method: "DELETE" });
}

export function deleteResumesBulk(resumeIds) {
  return request("/resumes/delete/bulk", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_ids: resumeIds }),
  });
}

export function getExtractedData(resumeId) {
  return request(`/resumes/${resumeId}/extracted`);
}

// ─── Evaluation ───

export function trainModels() {
  return request("/evaluation/train", { method: "POST" });
}

export function getEvaluationResults() {
  return request("/evaluation/results");
}

// ─── Taxonomy ───

export function getTaxonomy(category) {
  const query = category ? `?category=${category}` : "";
  return request(`/taxonomy${query}`);
}

export function addTaxonomySkill(name, category, aliases) {
  return request("/taxonomy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, category, aliases }),
  });
}

export function updateTaxonomySkill(id, name, category, aliases) {
  return request(`/taxonomy/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, category, aliases }),
  });
}

export function deleteTaxonomySkill(id) {
  return request(`/taxonomy/${id}`, { method: "DELETE" });
}

export function getTaxonomyCategories() {
  return request("/taxonomy/categories");
}
