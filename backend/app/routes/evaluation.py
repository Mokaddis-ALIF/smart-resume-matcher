"""
Model evaluation API endpoints.

POST   /api/evaluation/train     → Train all classifiers on the Kaggle dataset
GET    /api/evaluation/results   → Get evaluation metrics and model comparison
POST   /api/evaluation/classify  → Classify a single resume text with all models
"""
from flask import Blueprint, jsonify, request
from app.services.classifier import train_all_classifiers, train_structured_classifiers, get_evaluation_results, classify_resume

evaluation_bp = Blueprint("evaluation", __name__)


@evaluation_bp.route("/api/evaluation/train", methods=["POST"])
def train_models():
    """Train all classifiers on both datasets."""
    results = {}

    # Dataset 1: Resume text classification
    try:
        results["dataset1"] = train_all_classifiers()
        results["dataset1"]["dataset_name"] = "Resume Text Dataset (Kaggle)"
    except FileNotFoundError as e:
        results["dataset1"] = {"error": str(e)}

    # Dataset 2: Structured features classification
    try:
        results["dataset2"] = train_structured_classifiers()
        results["dataset2"]["dataset_name"] = "Candidate Job Role Dataset"
    except FileNotFoundError as e:
        results["dataset2"] = {"error": str(e)}

    if all("error" in v for v in results.values()):
        return jsonify({"error": "No datasets found"}), 404

    return jsonify({"message": "Training complete", **results})


@evaluation_bp.route("/api/evaluation/results", methods=["GET"])
def get_results():
    """Get saved evaluation results and model comparison metrics."""
    results = get_evaluation_results()
    if not results:
        return jsonify({"error": "No evaluation results found. Train the models first."}), 404

    return jsonify(results)


@evaluation_bp.route("/api/evaluation/classify", methods=["POST"])
def classify_single():
    """Classify a single resume text with all trained models."""
    data = request.get_json()
    resume_text = data.get("text", "")

    if not resume_text or len(resume_text) < 50:
        return jsonify({"error": "Resume text too short"}), 400

    try:
        predictions = classify_resume(resume_text)
        return jsonify({"predictions": predictions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
