"""
API documentation endpoint.

GET /api/docs → Returns full API documentation as JSON
"""
from flask import Blueprint, jsonify

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/api/docs", methods=["GET"])
def api_docs():
    """Return full API documentation."""
    return jsonify({
        "title": "Smart Resume Matching Tool API",
        "version": "1.0.0",
        "description": "Automated CV screening system using NLP and Machine Learning",
        "endpoints": {
            "health": {
                "GET /api/health": {
                    "description": "Check if API and database are running",
                    "response": {"status": "running", "database": "connected"}
                }
            },
            "jobs": {
                "POST /api/jobs": {
                    "description": "Create a new job posting",
                    "body": {
                        "title": "string (required)",
                        "company": "string (required)",
                        "description": "string (required)",
                        "requirements": {
                            "required_skills": ["string"],
                            "preferred_skills": ["string"],
                            "min_experience_years": "integer",
                            "education_level": "none | diploma | bachelors | masters | phd",
                            "education_field": "string"
                        },
                        "weights": {
                            "skills": "float (default 0.40)",
                            "experience": "float (default 0.30)",
                            "education": "float (default 0.15)",
                            "projects": "float (default 0.15)"
                        }
                    },
                    "response_code": 201
                },
                "GET /api/jobs": {
                    "description": "List all job postings",
                    "response": {"jobs": "array", "count": "integer"}
                },
                "GET /api/jobs/<id>": {
                    "description": "Get a single job posting with resume count",
                    "response": {"job": "object"}
                },
                "PUT /api/jobs/<id>": {
                    "description": "Update a job posting",
                    "body": "Partial job fields to update"
                },
                "DELETE /api/jobs/<id>": {
                    "description": "Delete a job and all associated resumes and match results"
                },
                "POST /api/jobs/<id>/match": {
                    "description": "Score all uploaded CVs against this job. Clears previous results and re-scores.",
                    "response": {
                        "results": "array of {resume_id, filename, candidate_name, overall_score, category}",
                        "summary": {"highly_qualified": "int", "qualified": "int", "not_qualified": "int"}
                    }
                },
                "GET /api/jobs/<id>/results": {
                    "description": "Get all match results for a job, sorted by score descending",
                    "response": {
                        "results": "array with score_breakdown, explanation, ml_predictions",
                        "summary": "category counts",
                        "total": "integer"
                    }
                }
            },
            "resumes": {
                "POST /api/jobs/<id>/resumes/upload": {
                    "description": "Upload a single CV (PDF/DOCX). Automatically parses and runs NLP pipeline.",
                    "body": "multipart/form-data with 'file' field",
                    "accepted_formats": ["pdf", "docx", "doc"],
                    "response_code": 201
                },
                "POST /api/jobs/<id>/resumes/upload/bulk": {
                    "description": "Upload multiple CVs at once",
                    "body": "multipart/form-data with 'files' field (multiple)",
                    "response": {"uploaded": "array", "errors": "array"}
                },
                "GET /api/jobs/<id>/resumes": {
                    "description": "List all resumes for a job",
                    "response": {"resumes": "array", "count": "integer"}
                },
                "GET /api/resumes/<id>": {
                    "description": "Get a single resume with parsed_data and nlp_data"
                },
                "DELETE /api/resumes/<id>": {
                    "description": "Delete a resume, its file, and match results"
                },
                "GET /api/resumes/<id>/extracted": {
                    "description": "Get NLP-extracted data (skills with confidence, entities, embeddings)"
                }
            },
            "evaluation": {
                "POST /api/evaluation/train": {
                    "description": "Train SVM, Random Forest, KNN, and Naive Bayes on the Kaggle dataset. Takes 30-60 seconds.",
                    "response": {
                        "results": "per-model metrics (accuracy, precision, recall, f1, confusion_matrix)",
                        "dataset_size": "integer",
                        "categories": "array of 24 job categories"
                    }
                },
                "GET /api/evaluation/results": {
                    "description": "Get saved evaluation metrics from last training run"
                },
                "POST /api/evaluation/classify": {
                    "description": "Classify a single resume text with all trained models",
                    "body": {"text": "string (resume text)"},
                    "response": {"predictions": "per-model category + confidence"}
                }
            }
        },
        "scoring": {
            "description": "Weighted scoring algorithm for matching CVs to jobs",
            "default_weights": {
                "skills": "40% — required/preferred skill overlap",
                "experience": "30% — years vs minimum requirement",
                "education": "15% — degree level and field match",
                "projects": "15% — technology overlap in projects"
            },
            "semantic_bonus": "Up to 5 extra points from BERT cosine similarity",
            "categories": {
                "highly_qualified": "score >= 75",
                "qualified": "50 <= score < 75",
                "not_qualified": "score < 50"
            }
        },
        "nlp_pipeline": {
            "text_extraction": "PyMuPDF (PDF) + python-docx (DOCX)",
            "section_parsing": "Regex-based heading detection and content splitting",
            "skill_extraction": "Custom taxonomy (130+ skills) with confidence scoring",
            "named_entities": "spaCy en_core_web_sm NER model",
            "embeddings": "Sentence-BERT (all-MiniLM-L6-v2, 384 dimensions)"
        }
    })
