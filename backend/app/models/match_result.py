"""
Match result document schema for MongoDB.

Example document in the "match_results" collection:
{
    "_id": ObjectId("..."),
    "job_id": ObjectId("..."),
    "resume_id": ObjectId("..."),
    "matched_at": "2026-06-19T10:30:00Z",

    "overall_score": 82.5,
    "category": "highly_qualified",

    "score_breakdown": {
        "skills": {
            "score": 85.0,
            "weight": 0.40,
            "weighted_score": 34.0,
            "matched": ["Python", "Flask", "MongoDB"],
            "missing": ["Docker"],
            "extra": ["React", "TypeScript"]
        },
        "experience": {
            "score": 90.0,
            "weight": 0.30,
            "weighted_score": 27.0,
            "required_years": 3,
            "candidate_years": 4,
            "relevant_roles": ["Software Engineer", "Backend Developer"]
        },
        "education": {
            "score": 70.0,
            "weight": 0.15,
            "weighted_score": 10.5,
            "required_level": "bachelors",
            "candidate_level": "masters",
            "field_match": True
        },
        "projects": {
            "score": 73.3,
            "weight": 0.15,
            "weighted_score": 11.0,
            "relevant_projects": ["E-commerce Platform"],
            "tech_overlap": ["Python", "Flask"]
        }
    },

    "explanation": "Strong candidate with 4 years of relevant experience..."
}
"""
from datetime import datetime, timezone


# Score thresholds for categorisation
CATEGORY_THRESHOLDS = {
    "highly_qualified": 75,  # score >= 75
    "qualified": 50,         # score >= 50
    "not_qualified": 0,      # score < 50
}


def get_category(score):
    """Determine candidate category based on overall score."""
    if score >= CATEGORY_THRESHOLDS["highly_qualified"]:
        return "highly_qualified"
    elif score >= CATEGORY_THRESHOLDS["qualified"]:
        return "qualified"
    else:
        return "not_qualified"


def create_match_result_doc(job_id, resume_id, overall_score, score_breakdown, explanation):
    """Create a new match result document."""
    return {
        "job_id": job_id,
        "resume_id": resume_id,
        "matched_at": datetime.now(timezone.utc).isoformat(),
        "overall_score": round(overall_score, 2),
        "category": get_category(overall_score),
        "score_breakdown": score_breakdown,
        "explanation": explanation,
    }
