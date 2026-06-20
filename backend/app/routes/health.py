from flask import Blueprint, jsonify
from app import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """Basic health check — confirms the API and database are running."""
    try:
        # Ping MongoDB to verify connection
        db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return jsonify({
        "status": "running",
        "database": db_status,
    })
