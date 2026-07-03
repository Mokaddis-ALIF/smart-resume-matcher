"""
Model evaluation API endpoints.

POST   /api/evaluation/train                 → Train all classifiers on both datasets
GET    /api/evaluation/results               → Get saved evaluation metrics
POST   /api/evaluation/classify?dataset=1|2  → Classify a single resume with all models
"""
from flask import Blueprint, jsonify, request
from app.services.classifier import (
    run_full_evaluation,
    get_evaluation_results,
    classify_resume,
)

evaluation_bp = Blueprint("evaluation", __name__)


@evaluation_bp.route("/api/evaluation/train", methods=["POST"])
def train_models():
    """Run the full evaluation pipeline: D1 + D2 leakage check + D2 raw + D2 clean."""
    try:
        results = run_full_evaluation()
        return jsonify({"message": "Training complete", **results})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Training failed: {str(e)}"}), 500


@evaluation_bp.route("/api/evaluation/results", methods=["GET"])
def get_results():
    """Get saved evaluation results (all datasets + leakage info)."""
    results = get_evaluation_results()
    if not results:
        return jsonify({"error": "No evaluation results found. Train the models first."}), 404
    return jsonify(results)


@evaluation_bp.route("/api/evaluation/classify", methods=["POST"])
def classify_single():
    """Classify a single resume text with all trained models.

    Query params:
        dataset (int, optional): 1 = AI Resume Screening (default),
                                 2 = resume_dataset_2.
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
