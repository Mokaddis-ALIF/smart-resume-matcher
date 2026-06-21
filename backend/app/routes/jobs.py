"""
Job posting API endpoints.

POST   /api/jobs                → Create a new job posting
GET    /api/jobs                → List all job postings
GET    /api/jobs/<id>           → Get a single job posting
PUT    /api/jobs/<id>           → Update a job posting
DELETE /api/jobs/<id>           → Delete a job posting
POST   /api/jobs/<id>/match    → Trigger matching for all CVs against this job
GET    /api/jobs/<id>/results  → Get all match results for this job
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app import db
from app.models.job import create_job_doc
from app.models.match_result import create_match_result_doc
from app.services.matcher import match_resume_to_job

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/api/jobs", methods=["POST"])
def create_job():
    """Create a new job posting."""
    data = request.get_json()

    # Validate required fields
    required = ["title", "company", "description", "requirements"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    job = create_job_doc(
        title=data["title"],
        company=data["company"],
        description=data["description"],
        requirements=data["requirements"],
    )

    # Allow custom weights if provided
    if "weights" in data:
        job["weights"] = data["weights"]

    result = db.jobs.insert_one(job)
    job["_id"] = str(result.inserted_id)

    return jsonify({"message": "Job created", "job": job}), 201


@jobs_bp.route("/api/jobs", methods=["GET"])
def list_jobs():
    """List all job postings."""
    jobs = []
    for job in db.jobs.find().sort("created_at", -1):
        job["_id"] = str(job["_id"])
        jobs.append(job)

    return jsonify({"jobs": jobs, "count": len(jobs)})


@jobs_bp.route("/api/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    """Get a single job posting by ID."""
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job ID"}), 400

    if not job:
        return jsonify({"error": "Job not found"}), 404

    job["_id"] = str(job["_id"])

    # Also return count of uploaded resumes for this job
    resume_count = db.resumes.count_documents({"job_id": job_id})
    job["resume_count"] = resume_count

    return jsonify({"job": job})


@jobs_bp.route("/api/jobs/<job_id>", methods=["PUT"])
def update_job(job_id):
    """Update a job posting."""
    data = request.get_json()

    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job ID"}), 400

    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Only update fields that are provided
    allowed_fields = ["title", "company", "description", "requirements", "weights", "status"]
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": updates})

    updated_job = db.jobs.find_one({"_id": ObjectId(job_id)})
    updated_job["_id"] = str(updated_job["_id"])

    return jsonify({"message": "Job updated", "job": updated_job})


@jobs_bp.route("/api/jobs/<job_id>", methods=["DELETE"])
def delete_job(job_id):
    """Delete a job posting and all associated resumes and match results."""
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job ID"}), 400

    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Delete all associated data
    db.match_results.delete_many({"job_id": job_id})
    db.resumes.delete_many({"job_id": job_id})
    db.jobs.delete_one({"_id": ObjectId(job_id)})

    return jsonify({"message": "Job and all associated data deleted"})


@jobs_bp.route("/api/jobs/<job_id>/match", methods=["POST"])
def trigger_matching(job_id):
    """Trigger matching for all uploaded CVs against this job.
    Scores each resume, stores results, and returns a summary.
    """
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job ID"}), 400

    if not job:
        return jsonify({"error": "Job not found"}), 404

    resumes = list(db.resumes.find({"job_id": job_id}))
    if len(resumes) == 0:
        return jsonify({"error": "No resumes uploaded for this job"}), 400

    # Clear previous match results for this job
    db.match_results.delete_many({"job_id": job_id})

    results = []
    for resume in resumes:
        # Only match parsed resumes
        if resume.get("status") != "parsed":
            continue

        # Run the matching engine
        match = match_resume_to_job(resume, job)

        # Store the result in MongoDB
        result_doc = create_match_result_doc(
            job_id=job_id,
            resume_id=str(resume["_id"]),
            overall_score=match["overall_score"],
            score_breakdown=match["score_breakdown"],
            explanation=match["explanation"],
        )
        result_doc["ml_predictions"] = match.get("ml_predictions", {})
        db.match_results.insert_one(result_doc)

        results.append({
            "resume_id": str(resume["_id"]),
            "filename": resume["filename"],
            "candidate_name": resume.get("parsed_data", {}).get("name", "Unknown"),
            "overall_score": match["overall_score"],
            "category": match["category"],
        })

    # Update matched count on the job
    db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"matched_count": len(results)}}
    )

    # Sort by score descending
    results.sort(key=lambda x: x["overall_score"], reverse=True)

    # Summary
    summary = {
        "highly_qualified": len([r for r in results if r["category"] == "highly_qualified"]),
        "qualified": len([r for r in results if r["category"] == "qualified"]),
        "not_qualified": len([r for r in results if r["category"] == "not_qualified"]),
    }

    return jsonify({
        "message": f"Matching complete — {len(results)} resumes scored",
        "results": results,
        "summary": summary,
    })


@jobs_bp.route("/api/jobs/<job_id>/results", methods=["GET"])
def get_results(job_id):
    """Get all match results for a job, sorted by score descending."""
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job ID"}), 400

    if not job:
        return jsonify({"error": "Job not found"}), 404

    results = []
    for result in db.match_results.find({"job_id": job_id}).sort("overall_score", -1):
        result["_id"] = str(result["_id"])

        # Attach resume name for display
        resume = db.resumes.find_one({"_id": ObjectId(result["resume_id"])})
        if resume:
            result["candidate_name"] = resume["parsed_data"].get("name", "Unknown")
            result["filename"] = resume["filename"]

        results.append(result)

    # Group by category
    summary = {
        "highly_qualified": len([r for r in results if r["category"] == "highly_qualified"]),
        "qualified": len([r for r in results if r["category"] == "qualified"]),
        "not_qualified": len([r for r in results if r["category"] == "not_qualified"]),
    }

    return jsonify({"results": results, "summary": summary, "total": len(results)})
