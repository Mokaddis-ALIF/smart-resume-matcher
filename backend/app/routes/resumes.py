"""
Resume API endpoints.

POST   /api/jobs/<job_id>/resumes/upload      → Upload a single CV for a job
POST   /api/jobs/<job_id>/resumes/upload/bulk  → Upload multiple CVs for a job
GET    /api/jobs/<job_id>/resumes              → List all resumes for a job
GET    /api/resumes/<id>                       → Get a single resume with parsed data
DELETE /api/resumes/<id>                       → Delete a resume
GET    /api/resumes/<id>/extracted             → Get NLP-extracted data for a resume
"""
import os
import uuid
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app import db
from app.config import Config
from app.models.resume import create_resume_doc
from app.services.parser import extract_text
from app.services.section_parser import parse_cv
from app.services.nlp_extractor import run_nlp_pipeline

resumes_bp = Blueprint("resumes", __name__)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file):
    """Save uploaded file with a unique name. Returns (saved_filename, file_format, file_path)."""
    original = file.filename
    extension = original.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}_{original}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file.save(file_path)
    return original, extension, file_path


def process_resume(resume_id, file_path, file_format):
    """Extract text from CV, parse it into structured data, and update the database."""
    try:
        # Update status to parsing
        db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {"status": "parsing"}}
        )

        # Step 1: Extract raw text from the file
        raw_text = extract_text(file_path, file_format)

        if not raw_text or len(raw_text.strip()) < 10:
            db.resumes.update_one(
                {"_id": ObjectId(resume_id)},
                {"$set": {"status": "failed", "raw_text": raw_text or ""}}
            )
            return False, "Could not extract meaningful text from the file"

        # Step 2: Parse the raw text into structured sections
        parsed_data = parse_cv(raw_text)

        # Step 3: Run NLP pipeline (entity recognition + skill extraction)
        nlp_data = run_nlp_pipeline(raw_text, parsed_data)

        # Step 4: Update the resume document with all extracted data
        db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {
                "status": "parsed",
                "raw_text": raw_text,
                "parsed_data": parsed_data,
                "nlp_data": nlp_data,
            }}
        )

        return True, "Resume parsed successfully"

    except Exception as e:
        db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {"status": "failed"}}
        )
        return False, str(e)


@resumes_bp.route("/api/jobs/<job_id>/resumes/upload", methods=["POST"])
def upload_resume(job_id):
    """Upload a single CV for a specific job. Automatically parses after upload."""
    # Verify job exists
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job ID"}), 400

    if not job:
        return jsonify({"error": "Job not found"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    filename, file_format, file_path = save_file(file)
    resume = create_resume_doc(
        job_id=job_id,
        filename=filename,
        file_format=file_format,
        file_path=file_path,
    )

    result = db.resumes.insert_one(resume)
    resume_id = str(result.inserted_id)

    # Automatically parse the resume
    success, message = process_resume(resume_id, file_path, file_format)

    # Fetch the updated resume to return
    updated_resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
    updated_resume["_id"] = str(updated_resume["_id"])

    status_code = 201 if success else 207  # 207 = partial success
    return jsonify({
        "message": message,
        "resume": updated_resume,
    }), status_code


@resumes_bp.route("/api/jobs/<job_id>/resumes/upload/bulk", methods=["POST"])
def upload_resumes_bulk(job_id):
    """Upload multiple CVs for a specific job. Automatically parses each after upload."""
    # Verify job exists
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job ID"}), 400

    if not job:
        return jsonify({"error": "Job not found"}), 404

    files = request.files.getlist("files")
    if not files or len(files) == 0:
        return jsonify({"error": "No files provided"}), 400

    uploaded = []
    errors = []

    for file in files:
        if file.filename == "":
            continue

        if not allowed_file(file.filename):
            errors.append({"filename": file.filename, "error": "File type not allowed"})
            continue

        filename, file_format, file_path = save_file(file)
        resume = create_resume_doc(
            job_id=job_id,
            filename=filename,
            file_format=file_format,
            file_path=file_path,
        )

        result = db.resumes.insert_one(resume)
        resume_id = str(result.inserted_id)

        # Automatically parse each resume
        success, message = process_resume(resume_id, file_path, file_format)

        updated_resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
        updated_resume["_id"] = str(updated_resume["_id"])

        if success:
            uploaded.append(updated_resume)
        else:
            errors.append({"filename": filename, "error": message, "resume": updated_resume})

    return jsonify({
        "message": f"{len(uploaded)} resume(s) uploaded and parsed",
        "uploaded": uploaded,
        "errors": errors,
    }), 201


@resumes_bp.route("/api/jobs/<job_id>/resumes", methods=["GET"])
def list_resumes(job_id):
    """List all resumes uploaded for a specific job."""
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job ID"}), 400

    if not job:
        return jsonify({"error": "Job not found"}), 404

    resumes = []
    for resume in db.resumes.find({"job_id": job_id}).sort("uploaded_at", -1):
        resume["_id"] = str(resume["_id"])
        resumes.append(resume)

    return jsonify({"resumes": resumes, "count": len(resumes)})


@resumes_bp.route("/api/resumes/<resume_id>", methods=["GET"])
def get_resume(resume_id):
    """Get a single resume with all parsed data."""
    try:
        resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
    except Exception:
        return jsonify({"error": "Invalid resume ID"}), 400

    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    resume["_id"] = str(resume["_id"])
    return jsonify({"resume": resume})


@resumes_bp.route("/api/resumes/<resume_id>", methods=["DELETE"])
def delete_resume(resume_id):
    """Delete a resume and its match results."""
    try:
        resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
    except Exception:
        return jsonify({"error": "Invalid resume ID"}), 400

    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    # Delete associated match results
    db.match_results.delete_many({"resume_id": resume_id})

    # Delete the file from disk
    if os.path.exists(resume["file_path"]):
        os.remove(resume["file_path"])

    db.resumes.delete_one({"_id": ObjectId(resume_id)})

    return jsonify({"message": "Resume deleted"})


@resumes_bp.route("/api/resumes/<resume_id>/extracted", methods=["GET"])
def get_extracted_data(resume_id):
    """Get NLP-extracted data for a resume.
    This will be fully implemented in Phase 3 — for now returns parsed data.
    """
    try:
        resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
    except Exception:
        return jsonify({"error": "Invalid resume ID"}), 400

    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    return jsonify({
        "resume_id": str(resume["_id"]),
        "filename": resume["filename"],
        "status": resume["status"],
        "parsed_data": resume["parsed_data"],
        "nlp_data": resume["nlp_data"],
    })
