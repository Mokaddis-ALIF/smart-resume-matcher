"""
Model evaluation API endpoints.

POST   /api/evaluation/train     → Train all classifiers on the Kaggle dataset
GET    /api/evaluation/results   → Get evaluation metrics and model comparison
POST   /api/evaluation/classify  → Classify a single resume text with all models
"""
from flask import Blueprint, jsonify, request
from app.services.classifier import train_all_classifiers, get_evaluation_results, classify_resume

evaluation_bp = Blueprint("evaluation", __name__)


@evaluation_bp.route("/api/evaluation/train", methods=["POST"])
def train_models():
    """Train all four classifiers on the Kaggle resume dataset.
    This takes 30-60 seconds depending on your machine.
    """
    try:
        results = train_all_classifiers()
        return jsonify({
            "message": "Training complete",
            **results,
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Training failed: {str(e)}"}), 500


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
