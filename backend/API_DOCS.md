# Smart Resume Matching Tool — API Documentation

Base URL: `http://localhost:5000/api`

---

## Health

### GET /api/health
Check if the API and database are running.

**Response:**
```json
{
  "status": "running",
  "database": "connected"
}
```

---

## Jobs

### POST /api/jobs
Create a new job posting.

**Request Body:**
```json
{
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "description": "Looking for an experienced Python developer...",
  "requirements": {
    "required_skills": ["Python", "Flask", "MongoDB"],
    "preferred_skills": ["Docker", "AWS"],
    "min_experience_years": 3,
    "education_level": "bachelors",
    "education_field": "Computer Science"
  }
}
```

**Response:** `201 Created`

### GET /api/jobs
List all job postings (sorted by newest first).

### GET /api/jobs/:id
Get a single job posting with resume count.

### PUT /api/jobs/:id
Update a job posting. Only provided fields are updated.

### DELETE /api/jobs/:id
Delete a job posting and all associated resumes and match results.

### POST /api/jobs/:id/match
Trigger matching for all uploaded CVs against this job. Scores each resume, stores results, and returns a ranked summary.

**Response:**
```json
{
  "message": "Matching complete — 5 resumes scored",
  "results": [
    {
      "resume_id": "...",
      "filename": "john_doe.pdf",
      "candidate_name": "John Doe",
      "overall_score": 82.5,
      "category": "highly_qualified"
    }
  ],
  "summary": {
    "highly_qualified": 2,
    "qualified": 2,
    "not_qualified": 1
  }
}
```

### GET /api/jobs/:id/results
Get all match results for a job, sorted by score descending. Includes score breakdowns, explanations, and ML predictions.

---

## Resumes

### POST /api/jobs/:job_id/resumes/upload
Upload a single CV (PDF or DOCX). Automatically parses and extracts structured data.

**Request:** `multipart/form-data` with field `file`

### POST /api/jobs/:job_id/resumes/upload/bulk
Upload multiple CVs at once.

**Request:** `multipart/form-data` with field `files` (multiple)

### GET /api/jobs/:job_id/resumes
List all resumes for a specific job.

### GET /api/resumes/:id
Get a single resume with all parsed and NLP-extracted data.

### DELETE /api/resumes/:id
Delete a resume and its associated match results.

### GET /api/resumes/:id/extracted
Get NLP-extracted data (skills with confidence, named entities, embeddings).

---

## Evaluation

### POST /api/evaluation/train
Train all four ML classifiers (SVM, Random Forest, KNN, Naive Bayes) on the Kaggle resume dataset. Takes 30-60 seconds.

**Response:**
```json
{
  "message": "Training complete",
  "results": {
    "SVM": {
      "accuracy": 66.4,
      "precision": 67.35,
      "recall": 66.4,
      "f1_score": 65.65,
      "train_time_seconds": 123.656,
      "cv_mean_accuracy": 66.13,
      "cv_std": 4.01
    }
  },
  "dataset_size": 2484,
  "train_size": 1987,
  "test_size": 497
}
```

### GET /api/evaluation/results
Get saved evaluation results including per-model metrics, per-class reports, and confusion matrices.

### POST /api/evaluation/classify
Classify a single resume text with all trained models.

**Request Body:**
```json
{
  "text": "Full resume text here..."
}
```

---

## Scoring Algorithm

The matching engine scores each CV against a job using four weighted categories:

| Category   | Weight | What it measures |
|------------|--------|-----------------|
| Skills     | 40%    | Required/preferred skill overlap |
| Experience | 30%    | Years vs minimum requirement |
| Education  | 15%    | Degree level and field match |
| Projects   | 15%    | Tech overlap in project work |

Plus a BERT semantic similarity bonus (up to 5 points).

**Categorisation thresholds:**
- Highly Qualified: score >= 75
- Qualified: score >= 50
- Not Qualified: score < 50

---

## Error Responses

All errors return JSON with an `error` field:
```json
{
  "error": "Job not found"
}
```

Common HTTP status codes:
- `400` — Invalid request (bad ID, missing fields)
- `404` — Resource not found
- `500` — Server error
