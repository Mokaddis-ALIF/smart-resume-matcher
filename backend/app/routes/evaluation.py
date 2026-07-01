"""
Model evaluation API endpoints.

POST   /api/evaluation/train                     → Train all classifiers on both datasets
GET    /api/evaluation/results                   → Get evaluation metrics and model comparison
POST   /api/evaluation/classify?dataset=1|2      → Classify a single resume with all models
"""
from flask import Blueprint, jsonify, request
from app.services.classifier import (
    train_ai_screening_classifiers,
    train_structured_classifiers,
    get_evaluation_results,
    classify_resume,
)

evaluation_bp = Blueprint("evaluation", __name__)


@evaluation_bp.route("/api/evaluation/train", methods=["POST"])
def train_models():
    """Train all classifiers on both datasets.

    Each dataset is caught independently so a missing CSV or trainer failure
    on one side doesn't block the other.
    """
    results = {}

    # Dataset 1: AI Resume Screening
    try:
        results["dataset1"] = train_ai_screening_classifiers()
    except FileNotFoundError as e:
        results["dataset1"] = {"error": str(e)}
    except Exception as e:
        results["dataset1"] = {"error": f"Training failed: {str(e)}"}

    # Dataset 2: resume_data.csv
    try:
        results["dataset2"] = train_structured_classifiers()
    except FileNotFoundError as e:
        results["dataset2"] = {"error": str(e)}
    except Exception as e:
        results["dataset2"] = {"error": f"Training failed: {str(e)}"}

    if all("error" in v for v in results.values()):
        return jsonify({"error": "Training failed on both datasets", **results}), 500

    return jsonify({"message": "Training complete", **results})


@evaluation_bp.route("/api/evaluation/results", methods=["GET"])
def get_results():
    """Get saved evaluation results from both datasets."""
    results = get_evaluation_results()
    if not results:
        return jsonify({"error": "No evaluation results found. Train the models first."}), 404
    return jsonify(results)


@evaluation_bp.route("/api/evaluation/classify", methods=["POST"])
def classify_single():
    """Classify a single resume text with all trained models.

    Query params:
        dataset (int, optional): 1 = AI Resume Screening (default),
                                 2 = resume_data.csv.
    """
    data = request.get_json() or {}
    resume_text = data.get("text", "")

    try:
        dataset = int(request.args.get("dataset", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "dataset must be 1 or 2"}), 400

    if dataset not in (1, 2):
        return jsonify({"error": "dataset must be 1 or 2"}), 400

    if not resume_text or len(resume_text) < 50:
        return jsonify({"error": "Resume text too short"}), 400

    try:
        predictions = classify_resume(resume_text, dataset=dataset)
        return jsonify({"predictions": predictions, "dataset": dataset})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
