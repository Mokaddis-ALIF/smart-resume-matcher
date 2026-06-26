"""
Job posting document schema for MongoDB.

Example document in the "jobs" collection:
{
    "_id": ObjectId("..."),
    "title": "Senior Backend Developer",
    "created_at": "2026-06-19T10:30:00Z",

    "description": "We are looking for a senior backend developer...",

    "requirements": {
        "required_skills": ["Python", "Flask", "MongoDB", "Docker"],
        "preferred_skills": ["Kubernetes", "AWS", "Redis"],
        "min_experience_years": 3,
        "education_level": "bachelors",
        "education_field": "Computer Science"
    },

    "weights": {
        "skills": 0.40,
        "experience": 0.30,
        "education": 0.15,
        "projects": 0.15
    },

    "matched_count": 12,
    "status": "active"
}
"""
from datetime import datetime, timezone


DEFAULT_WEIGHTS = {
    "skills": 0.40,
    "experience": 0.30,
    "education": 0.15,
    "projects": 0.15,
}


def create_job_doc(title, description, requirements, soft_skills=None, reference=None):
    """Create a new job posting document."""
    return {
        "reference": reference,
        "title": title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "description": description,
        "requirements": {
            "required_skills": requirements.get("required_skills", []),
            "preferred_skills": requirements.get("preferred_skills", []),
            "min_experience_years": requirements.get("min_experience_years", 0),
            "education_level": requirements.get("education_level", None),
            "education_field": requirements.get("education_field", None),
        },
        "soft_skills": soft_skills or [],
        "weights": DEFAULT_WEIGHTS.copy(),
        "matched_count": 0,
        "status": "active",
    }


def generate_reference(db):
    """Generate the next job reference number (JOB-001, JOB-002, etc.)."""
    last_job = db.jobs.find_one(
        {"reference": {"$exists": True, "$ne": None}},
        sort=[("reference", -1)]
    )
    if last_job and last_job.get("reference"):
        try:
            num = int(last_job["reference"].split("-")[1])
            return f"JOB-{num + 1:03d}"
        except (IndexError, ValueError):
            pass

    # Count existing jobs as fallback
    count = db.jobs.count_documents({})
    return f"JOB-{count + 1:03d}"
