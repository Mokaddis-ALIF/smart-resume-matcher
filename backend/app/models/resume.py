"""
Resume document schema for MongoDB.

Each resume belongs to a specific job posting. CVs are uploaded
against a job and scored against that job's requirements.

Example document in the "resumes" collection:
{
    "_id": ObjectId("..."),
    "job_id": ObjectId("..."),
    "filename": "john_doe_cv.pdf",
    "file_format": "pdf",
    "file_path": "uploads/abc123_john_doe_cv.pdf",
    "uploaded_at": "2026-06-19T10:30:00Z",
    "status": "parsed",

    "raw_text": "Full extracted text from the CV...",

    "parsed_data": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+44 7123 456789",
        "location": "Bristol, UK",
        "summary": "Experienced software engineer with...",

        "skills": ["Python", "React", "Docker", "PostgreSQL"],

        "experience": [
            {
                "job_title": "Software Engineer",
                "company": "Tech Corp",
                "start_date": "2022-01",
                "end_date": "2025-06",
                "duration_months": 42,
                "description": "Developed microservices..."
            }
        ],

        "education": [
            {
                "degree": "MSc",
                "field": "Data Science",
                "institution": "University of Bristol",
                "year": 2025
            }
        ],

        "projects": [
            {
                "title": "E-commerce Platform",
                "technologies": ["Python", "Flask", "MongoDB"],
                "description": "Built a full-stack..."
            }
        ]
    },

    "nlp_data": {
        "extracted_skills": [
            {"skill": "Python", "confidence": 0.95, "source": "skills_section"},
            {"skill": "Docker", "confidence": 0.87, "source": "experience"}
        ],
        "entities": [
            {"text": "Tech Corp", "label": "ORG"},
            {"text": "University of Bristol", "label": "EDU"}
        ],
        "embedding": [0.021, -0.035, ...]
    }
}
"""
from datetime import datetime, timezone


def create_resume_doc(job_id, filename, file_format, file_path):
    """Create a new resume document linked to a specific job."""
    return {
        "job_id": job_id,
        "filename": filename,
        "file_format": file_format,
        "file_path": file_path,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "status": "uploaded",  # uploaded → parsing → parsed → failed
        "raw_text": None,
        "parsed_data": {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
            "summary": None,
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
        },
        "nlp_data": {
            "extracted_skills": [],
            "entities": [],
            "embedding": [],
        },
    }
